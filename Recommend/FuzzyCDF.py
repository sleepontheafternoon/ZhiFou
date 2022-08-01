import numpy as np
from scipy import stats
from collections import namedtuple
from Parameter_evaluate import update_theta,update_A_B,update_variance,update_slip_guess

hyper_para = namedtuple("hyperparameters",["sig_a", "mu_a", "sig_b", "mu_b", "max_s", "min_s", "max_g", "min_g", "mu_theta", "sig_theta"])
default_hyper = hyper_para(1, 0, 1, 0, 0.6, 0, 0.6, 0, 0, 1)


def init_parameters(stu_num, prob_num, know_num, args):  # initialize FuzzyCDF parameters
    a = stats.lognorm.rvs(s=args.sig_a, loc=0, scale=np.exp(args.mu_a), size=(stu_num, know_num))
    b = stats.norm.rvs(loc=args.mu_b, scale=args.sig_b, size=(stu_num, know_num))
    slip = stats.beta.rvs(a=1, b=2, size=prob_num) * (args.max_s - args.min_s) + args.min_s
    guess = stats.beta.rvs(a=1, b=2, size=prob_num) * (args.max_g - args.min_g) + args.min_g
    theta = stats.norm.rvs(loc=args.mu_theta, scale=args.sig_theta, size=stu_num)
    variance = 1 / stats.gamma.rvs(a=4, scale=1 / 6, size=1)
    return a, b, slip, guess, theta, variance



class CDM(object):
    def __init__(self, *args, **kwargs) -> ...:
        pass

    def train(self, *args, **kwargs) -> ...:
        raise NotImplementedError

    def eval(self, *args, **kwargs) -> ...:
        raise NotImplementedError

    def save(self, *args, **kwargs) -> ...:
        raise NotImplementedError

    def load(self, *args, **kwargs) -> ...:
        raise NotImplementedError





class FuzzyCDF(CDM):
    """
    FuzzyCDF model, training (MCMC) and testing methods
    :param R (array): response matrix, shape = (stu_num, prob_num)
    :param q_m (array): Q matrix, shape = (prob_num, know_num)
    :param stu_num (int): number of students
    :param prob_num (int): number of problems
    :param know_num (int): number of knowledge
    :param obj_prob_index (array): index of all objective problems, shape = (number, )
    :param sub_prob_index (array): index of all subjective problems, shape = (number, )
    :param skip_value (int): skip value in response matrix
    :param args: all hyper-parameters
    """

    def __init__(self, R, q_m, stu_num, prob_num, know_num, obj_prob_index, sub_prob_index, skip_value=-1,
                 args=default_hyper):
        self.args = args
        self.R, self.q_m, self.stu_num, self.prob_num, self.know_num = R, q_m, stu_num, prob_num, know_num
        self.a, self.b, self.slip, self.guess, self.theta, self.variance = init_parameters(stu_num, prob_num, know_num,
                                                                                           self.args)
        self.obj_prob_index, self.sub_prob_index, self.skip_value = obj_prob_index, sub_prob_index, skip_value

    def train(self, epoch, burnin) -> ...:
        A, B, slip, guess = np.copy(self.a), np.copy(self.b), np.copy(self.slip), np.copy(self.guess)
        theta, variance = np.copy(self.theta), np.copy(self.variance)
        estimate_A, estimate_B, estimate_slip, estimate_guess, estimate_theta, estimate_variance = 0, 0, 0, 0, 0, 0
        for iteration in range(epoch):
            update_A_B(A, B, theta, slip, guess, variance, self.R, self.q_m, self.obj_prob_index, self.sub_prob_index,
                       self.skip_value, self.args)
            update_theta(A, B, theta, slip, guess, variance, self.R, self.q_m, self.obj_prob_index, self.sub_prob_index,
                         self.skip_value, self.args)
            update_slip_guess(A, B, theta, slip, guess, variance, self.R, self.q_m, self.obj_prob_index,
                              self.sub_prob_index,
                              self.skip_value, self.args)
            variance = update_variance(A, B, theta, slip, guess, variance, self.R, self.q_m, self.obj_prob_index,
                                       self.sub_prob_index,
                                       self.skip_value)
            if iteration >= burnin:
                estimate_A += A
                estimate_B += B
                estimate_slip += slip
                estimate_guess += guess
                estimate_theta += theta
                estimate_variance += variance
        self.a, self.b, self.slip, self.guess, self.theta, self.variance = estimate_A / (epoch - burnin), estimate_B / (
            epoch - burnin), estimate_slip / (epoch - burnin), estimate_guess / (epoch - burnin), estimate_theta \
            / (epoch - burnin), estimate_variance / (epoch - burnin)
