import time

import utils
from models.model import Model
from models.nri.data_cleaner import clean_data
from models.nri.nri_train_test import train_test
from result_saver import ResultSaver


class NRI(Model):
    def __init__(self, config: utils.dotdict, result_saver: ResultSaver):
        super().__init__(config, result_saver)

        self.verbose = config.verbose
        self.num_layers = config.num_layers
        self.model_choice = config.model
        self.lr = config.lr
        self.lam = config.lam
        self.lam_ridge = config.lam_ridge
        self.max_iter = config.max_iter

    def _algorithm(self, series, coef_mat, edges) -> tuple:
        # Set seeds
        self.set_seeds()

        # Dataset creation
        train_loader, valid_loader, test_loader = clean_data(self.config, series, coef_mat, edges)

        # Train NRI model
        start_time = time.time()
        GC_est, results_ = train_test(self.config, train_loader, valid_loader, test_loader)
        results = {set_name+'_'+metric_name:values for set_name,v in results_.items() for metric_name,values in v.items()}

        # Verify learned Granger causality
        accuracy = self._calculate_accuracy(coef_mat, GC_est)
        results.update({'GC_est': GC_est.tolist()})
        results.update({'accuracy': accuracy})
        results.update({'time': time.time()-start_time})

        return accuracy, results
