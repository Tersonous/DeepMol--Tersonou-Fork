import uuid
from abc import abstractmethod
from typing import Union

import numpy as np
from imblearn import over_sampling, under_sampling, combine
from numpy.random import RandomState
from sklearn.cluster import KMeans

from deepmol.datasets import Dataset


class ImbalancedLearn(object):
    """
    Class for dealing with imbalanced datasets.

    A ImbalancedLearn sampler receives a Dataset object and performs over/under sampling.

    Subclasses need to implement a _sample method to perform over/under sampling.
    """

    def __init__(self):
        """
        Initialize the ImbalancedLearn sampler.
        """
        if self.__class__ == ImbalancedLearn:
            raise Exception('Abstract class ImbalancedLearn should not be instantiated')

        self.features = None
        self.y = None

    def sample(self, train_dataset: Dataset):
        """
        Sample the dataset.
        """
        self.features = train_dataset.X
        self.y = train_dataset.y
        features, y = self._sample()
        train_dataset._X = features
        train_dataset._y = y
        # TODO: how to keep track of which samples were over / under sampled (to ad/remove ids, mols and smiles)
        return train_dataset

    @abstractmethod
    def _sample(self):
        """
        Perform over/under sampling.
        """


#########################################
# OVER-SAMPLING
#########################################

class RandomOverSampler(ImbalancedLearn):
    """
    Class to perform naive random over-sampling.

    Wrapper around ImbalancedLearn RandomOverSampler
    (https://imbalanced-learn.readthedocs.io/en/stable/generated/imblearn.over_sampling.RandomOverSampler.html)

    Object to over-sample the minority class(es) by picking samples at random with replacement.
    """

    def __init__(self,
                 sampling_strategy: Union[float, str, dict, callable] = "auto",
                 random_state: Union[int, RandomState] = None):
        """
        Initialize the RandomOverSampler.

        Parameters
        ----------
        sampling_strategy: Union[float, str, dict, callable]
            Sampling information to resample the data set.

            When float, it corresponds to the desired ratio of the number of samples in the minority class over
            the number of samples in the majority class after resampling.

            When str, specify the class targeted by the resampling. The number of samples in the different classes
            will be equalized. Possible choices are:
                'minority': resample only the minority class;
                'not minority': resample all classes but the minority class;
                'not majority': resample all classes but the majority class;
                'all': resample all classes;
                'auto': equivalent to 'not majority'.

            When dict, the keys correspond to the targeted classes. The values correspond to the desired number of
            samples for each targeted class.

            When callable, function taking y and returns a dict. The keys correspond to the targeted classes.
            The values correspond to the desired number of samples for each class.
        random_state: Union[int, RandomState]
            Control the randomization of the algorithm.

            If int, random_state is the seed used by the random number generator;
            If RandomState instance, random_state is the random number generator;
            If None, the random number generator is the RandomState instance used by np.random.
        """
        super().__init__()
        self.sampling_strategy = sampling_strategy
        self.random_state = random_state

    def _sample(self):
        """
        Returns features resampled and y resampled.
        """
        ros = over_sampling.RandomOverSampler(sampling_strategy=self.sampling_strategy, random_state=self.random_state)
        return ros.fit_resample(self.features, self.y)


class SMOTE(ImbalancedLearn):
    """
    Class to perform Synthetic Minority Oversampling Technique (SMOTE) over-sampling.

    Wrapper around ImbalancedLearn SMOTE
    (https://imbalanced-learn.org/stable/generated/imblearn.over_sampling.SMOTE.html)
    """

    def __init__(self,
                 sampling_strategy: Union[float, str, dict, callable] = "auto",
                 random_state: Union[int, RandomState] = None,
                 k_neighbors: int = 5,
                 n_jobs: int = None):
        """
        Initialize the SMOTE.

        Parameters
        ----------
        sampling_strategy: Union[float, str, dict, callable]
            Sampling information to resample the data set.

            When float, it corresponds to the desired ratio of the number of samples in the minority class over
            the number of samples in the majority class after resampling.

            When str, specify the class targeted by the resampling. The number of samples in the different classes
            will be equalized. Possible choices are:
                'minority': resample only the minority class;
                'not minority': resample all classes but the minority class;
                'not majority': resample all classes but the majority class;
                'all': resample all classes;
                'auto': equivalent to 'not majority'.

            When dict, the keys correspond to the targeted classes. The values correspond to the desired number of
            samples for each targeted class.

            When callable, function taking y and returns a dict. The keys correspond to the targeted classes.
            The values correspond to the desired number of samples for each class.
        random_state: Union[int, RandomState]
            Control the randomization of the algorithm.

            If int, random_state is the seed used by the random number generator;

            If RandomState instance, random_state is the random number generator;

            If None, the random number generator is the RandomState instance used by np.random.
        k_neighbors: int
            Number of nearest neighbours to used to construct synthetic samples.
        n_jobs: int
            Number of CPU cores used during the cross-validation loop. None means 1 unless in a
            joblib.parallel_backend context. -1 means using all processors.
        """
        super().__init__()
        self.sampling_strategy = sampling_strategy
        self.random_state = random_state
        self.k_neighbors = k_neighbors
        self.n_jobs = n_jobs

    def _sample(self):
        """
        Returns features resampled and y resampled.
        """
        ros = over_sampling.SMOTE(sampling_strategy=self.sampling_strategy,
                                  random_state=self.random_state,
                                  k_neighbors=self.k_neighbors,
                                  n_jobs=self.n_jobs)
        return ros.fit_resample(self.features, self.y)


#########################################
# UNDER-SAMPLING
#########################################

class ClusterCentroids(ImbalancedLearn):
    """
    Class to perform ClusterCentroids under-sampling.

    Wrapper around ImbalancedLearn ClusterCentroids
    (https://imbalanced-learn.org/stable/generated/imblearn.under_sampling.ClusterCentroids.html)

    Perform under-sampling by generating centroids based on clustering.
    """

    def __init__(self,
                 sampling_strategy: Union[float, str, dict, callable] = "auto",
                 random_state: Union[int, RandomState] = None,
                 estimator: callable = KMeans(),
                 voting: str = 'auto'):
        """
        Initialize the ClusterCentroids.

        Parameters
        ----------
        sampling_strategy: Union[float, str, dict, callable]
            Sampling information to resample the data set.

            When float, it corresponds to the desired ratio of the number of samples in the minority class over
            the number of samples in the majority class after resampling.

            When str, specify the class targeted by the resampling. The number of samples in the different classes
            will be equalized. Possible choices are:
                'minority': resample only the minority class;
                'not minority': resample all classes but the minority class;
                'not majority': resample all classes but the majority class;
                'all': resample all classes;
                'auto': equivalent to 'not majority'.

            When dict, the keys correspond to the targeted classes. The values correspond to the desired number of
            samples for each targeted class.

            When callable, function taking y and returns a dict. The keys correspond to the targeted classes.
            The values correspond to the desired number of samples for each class.
        random_state: Union[int, RandomState]
            Control the randomization of the algorithm.

            If int, random_state is the seed used by the random number generator;

            If RandomState instance, random_state is the random number generator;

            If None, the random number generator is the RandomState instance used by np.random.
        estimator: object, default=KMeans()
            Pass a sklearn.cluster.KMeans estimator.
        voting: str
            Voting strategy to generate the new samples:

            If 'hard', the nearest-neighbors of the centroids found using the clustering algorithm will be used.

            If 'soft', the centroids found by the clustering algorithm will be used.

            If 'auto', if the input is sparse, it will default on 'hard' otherwise, 'soft' will be used.
        """
        super().__init__()
        self.sampling_strategy = sampling_strategy
        self.random_state = random_state
        self.estimator = estimator
        self.voting = voting

    def _sample(self):
        """
        Returns features resampled and y resampled.
        """
        ros = under_sampling.ClusterCentroids(sampling_strategy=self.sampling_strategy,
                                              random_state=self.random_state,
                                              estimator=self.estimator,
                                              voting=self.voting)
        return ros.fit_resample(self.features, self.y)


class RandomUnderSampler(ImbalancedLearn):
    """
    Class to perform RandomUnderSampler under-sampling.

    Wrapper around ImbalancedLearn RandomUnderSampler
    (https://imbalanced-learn.org/stable/generated/imblearn.under_sampling.RandomUnderSampler.html)

    Under-sample the majority class(es) by randomly picking samples with or without replacement.
    """

    def __init__(self,
                 sampling_strategy: Union[float, str, dict, callable] = "auto",
                 random_state: Union[int, RandomState] = None,
                 replacement: bool = False):
        """
        Initialize the RandomUnderSampler.

        Parameters
        ----------
        sampling_strategy: Union[float, str, dict, callable]
            Sampling information to resample the data set.

            When float, it corresponds to the desired ratio of the number of samples in the minority class over
            the number of samples in the majority class after resampling.

            When str, specify the class targeted by the resampling. The number of samples in the different classes
            will be equalized. Possible choices are:
                'minority': resample only the minority class;
                'not minority': resample all classes but the minority class;
                'not majority': resample all classes but the majority class;
                'all': resample all classes;
                'auto': equivalent to 'not majority'.

            When dict, the keys correspond to the targeted classes. The values correspond to the desired number of
            samples for each targeted class.

            When callable, function taking y and returns a dict. The keys correspond to the targeted classes.
            The values correspond to the desired number of samples for each class.
        random_state: Union[int, RandomState]
            Control the randomization of the algorithm.

            If int, random_state is the seed used by the random number generator;

            If RandomState instance, random_state is the random number generator;

            If None, the random number generator is the RandomState instance used by np.random.
        replacement: bool
            Whether the sample is with or without replacement.
        """
        super().__init__()
        self.sampling_strategy = sampling_strategy
        self.random_state = random_state
        self.replacement = replacement

    def _sample(self):
        """
        Returns features resampled and y resampled.
        """
        ros = under_sampling.RandomUnderSampler(sampling_strategy=self.sampling_strategy,
                                                random_state=self.random_state,
                                                replacement=self.replacement)
        return ros.fit_resample(self.features, self.y)


#########################################
# COMBINATION OF OVER AND UNDER-SAMPLING
#########################################

class SMOTEENN(ImbalancedLearn):
    """
    Class to perform SMOTEENN over and under-sampling.

    Wrapper around ImbalancedLearn SMOTEENN
    (https://imbalanced-learn.org/stable/generated/imblearn.combine.SMOTEENN.html)

    Over-sampling using SMOTE and cleaning using ENN.
    Combine over and under-sampling using SMOTE and Edited Nearest Neighbours.
    """

    def __init__(self,
                 sampling_strategy: Union[float, str, dict, callable] = "auto",
                 random_state: Union[int, RandomState] = None,
                 smote: callable = None,
                 enn: callable = None,
                 n_jobs: int = None):
        """
        Initialize the SMOTEENN.

        Parameters
        ----------
        sampling_strategy: Union[float, str, dict, callable]
            Sampling information to resample the data set.

            When float, it corresponds to the desired ratio of the number of samples in the minority class over
            the number of samples in the majority class after resampling.

            When str, specify the class targeted by the resampling. The number of samples in the different classes
            will be equalized. Possible choices are:
                'minority': resample only the minority class;
                'not minority': resample all classes but the minority class;
                'not majority': resample all classes but the majority class;
                'all': resample all classes;
                'auto': equivalent to 'not majority'.

            When dict, the keys correspond to the targeted classes. The values correspond to the desired number of
            samples for each targeted class.

            When callable, function taking y and returns a dict. The keys correspond to the targeted classes.
            The values correspond to the desired number of samples for each class.
        random_state: Union[int, RandomState]
            Control the randomization of the algorithm.

            If int, random_state is the seed used by the random number generator;

            If RandomState instance, random_state is the random number generator;

            If None, the random number generator is the RandomState instance used by np.random.
        smote: callable
            The imblearn.over_sampling.SMOTE object to use. If not given, a imblearn.over_sampling.SMOTE object
            with default parameters will be given.
        enn: callable
            The imblearn.under_sampling.EditedNearestNeighbours object to use. If not given, a
            imblearn.under_sampling.EditedNearestNeighbours object with sampling strategy=’all’ will be given.
        n_jobs: int
            Number of CPU cores used during the cross-validation loop. None means 1 unless in a
            joblib.parallel_backend context. -1 means using all processors.
        """
        super().__init__()
        self.sampling_strategy = sampling_strategy
        self.random_state = random_state
        self.smote = smote
        self.enn = enn
        self.n_jobs = n_jobs

    def _sample(self):
        """
        Returns features resampled and y resampled.
        """
        ros = combine.SMOTEENN(sampling_strategy=self.sampling_strategy,
                               random_state=self.random_state,
                               smote=self.smote,
                               enn=self.enn,
                               n_jobs=self.n_jobs)
        return ros.fit_resample(self.features, self.y)


class SMOTETomek(ImbalancedLearn):
    """
    Class to perform SMOTETomek over and under-sampling.

    Wrapper around ImbalancedLearn SMOTETomek
    (https://imbalanced-learn.org/stable/generated/imblearn.combine.SMOTETomek.html)

    Over-sampling using SMOTE and cleaning using Tomek links.
    Combine over- and under-sampling using SMOTE and Tomek links.
    """

    def __init__(self,
                 sampling_strategy: Union[float, str, dict, callable] = "auto",
                 random_state: Union[int, RandomState] = None,
                 smote: callable = None,
                 tomek: callable = None,
                 n_jobs: int = None):
        """
        Initialize the SMOTETomek.

        Parameters
        ----------
        sampling_strategy: Union[float, str, dict, callable]
            Sampling information to resample the data set.

            When float, it corresponds to the desired ratio of the number of samples in the minority class over
            the number of samples in the majority class after resampling.

            When str, specify the class targeted by the resampling. The number of samples in the different classes
            will be equalized. Possible choices are:
                'minority': resample only the minority class;
                'not minority': resample all classes but the minority class;
                'not majority': resample all classes but the majority class;
                'all': resample all classes;
                'auto': equivalent to 'not majority'.

            When dict, the keys correspond to the targeted classes. The values correspond to the desired number of
            samples for each targeted class.

            When callable, function taking y and returns a dict. The keys correspond to the targeted classes.
            The values correspond to the desired number of samples for each class.
        random_state: Union[int, RandomState]
            Control the randomization of the algorithm.

            If int, random_state is the seed used by the random number generator;

            If RandomState instance, random_state is the random number generator;

            If None, the random number generator is the RandomState instance used by np.random.
        smote: callable
            The imblearn.over_sampling.SMOTE object to use. If not given, a imblearn.over_sampling.SMOTE object
            with default parameters will be given.
        tomek: callable
            The imblearn.under_sampling.TomekLinks object to use. If not given, a imblearn.under_sampling.TomekLinks
            object with sampling strategy="all" will be given.
        n_jobs: int
            Number of CPU cores used during the cross-validation loop. None means 1 unless in a
            joblib.parallel_backend context. -1 means using all processors.
        """
        super().__init__()
        self.replacement = None
        self.sampling_strategy = sampling_strategy
        self.random_state = random_state
        self.smote = smote
        self.tomek = tomek
        self.n_jobs = n_jobs

    def _sample(self):
        """
        Returns features resampled and y resampled.
        """
        ros = combine.SMOTETomek(sampling_strategy=self.sampling_strategy,
                                 random_state=self.random_state,
                                 smote=self.replacement,
                                 tomek=self.tomek,
                                 n_jobs=self.n_jobs)
        return ros.fit_resample(self.features, self.y)
