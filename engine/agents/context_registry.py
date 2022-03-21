from typing import List, Any, Dict, Tuple, Optional
from abc import abstractmethod, abstractproperty
from xml.sax.handler import feature_external_ges


class FeatureWeight:
    def __init__(self, weight, bias) -> None:
        self.__weight: float = weight
        self.__bias: float = bias

    @property
    def weight(self):
        return self.__weight

    @property
    def bias(self):
        return self.__bias


class FeatureDefinition:
    def __init__(self, label: str) -> None:
        self.__label: str = label

    @property
    def label(self) -> str:
        return self.__label

    @abstractproperty
    def possible_values(self) -> List[Any]:
        return []

    @abstractmethod
    def calculateValue(self, featureWeight: FeatureWeight, value: Any) -> float:
        return 0


class ScalarFeature(FeatureDefinition):
    def __init__(self, label: str) -> None:
        super().__init__(label)

    def createPossibleFeatures(self) -> List[str]:
        return [self.label]

    def calculateValue(self, featureWeight: FeatureWeight, value: Any) -> float:
        return featureWeight.weight * value + featureWeight.bias

    @property
    def possible_values(self) -> List[Any]:
        return [None]


class CategoricalFeature(FeatureDefinition):
    def __init__(self, label: str, possible_values: List[Any]) -> None:
        super().__init__(label)
        self.__values: List[Any] = possible_values

    def calculateValue(self, featureWeight: FeatureWeight, value: Any) -> float:
        return 1 * featureWeight.weight + featureWeight.bias

    @property
    def possible_values(self) -> List[Any]:
        return self.__values


class WeightVector:
    def __init__(self, features: Dict[str, FeatureDefinition]) -> None:
        self.__feature_definitions: Dict[str, FeatureDefinition] = features
        self.__scalar_feature_weight: Dict[str, FeatureWeight] = {}
        self.__categorical_feature_weight: Dict[Tuple[str, Any], FeatureWeight] = {}

    def registerScalarFeatureWeights(
        self, label: str, weight: float, bias: float
    ) -> None:
        if label not in self.__feature_definitions:
            raise Exception("Registering weights for feature not registered...")

        if not isinstance(self.__feature_definitions[label], ScalarFeature):
            raise Exception("Attempting to register weights on non scalar feature")

        self.__scalar_feature_weight[label] = FeatureWeight(weight, bias)

    def registerCategorialFeatureWeights(
        self, label: str, value: Any, weight: float, bias: float
    ) -> None:
        if label not in self.__feature_definitions:
            raise Exception(
                "Attempting to register weights for feature not registered..."
            )

        if not isinstance(self.__feature_definitions[label], CategoricalFeature):
            raise Exception("Attempting to register weights on non categorical feature")

        self.__categorical_feature_weight[(label, value)] = FeatureWeight(weight, bias)

    def calculate_salience(self, features_values: Dict[str, Any]) -> float:
        for label in features_values.keys():
            if label not in self.__feature_definitions:
                raise Exception(
                    "Attempting to calculate salience with feature not registered"
                )

        sum = 0

        for label, feature_defintion in self.__feature_definitions.items():
            if isinstance(feature_defintion, ScalarFeature):
                sum += feature_defintion.calculateValue(
                    self.__scalar_feature_weight[label], features_values[label]
                )
            elif isinstance(feature_defintion, CategoricalFeature):
                if features_values[label] is None:
                    continue

                sum += feature_defintion.calculateValue(
                    self.__categorical_feature_weight[label, features_values[label]],
                    features_values[label],
                )

        return sum

    def get_scalar_features(self) -> Dict[str, FeatureWeight]:
        return self.__scalar_feature_weight

    def get_categorical_features(self) -> Dict[Tuple[str, Any], FeatureWeight]:
        return self.__categorical_feature_weight

    def __str__(self) -> str:
        res = ""
        for label, value in self.__scalar_feature_weight.items():
            res += f"[{label} => b:{value.bias} w:{value.weight}]"

        for label, value in self.__categorical_feature_weight.items():
            res += f"[{label[0]}, {label[1]} => b:{value.bias} w:{value.weight}]"
        return res


class ContextRegistry:
    def __init__(self) -> None:
        self.__feature_definitions: Dict[str, FeatureDefinition] = {}

    @property
    def feature_labels(self) -> List[str]:
        return list(self.__feature_definitions.keys())

    def registerScalarFeature(self, label: str) -> None:
        self.__feature_definitions[label] = ScalarFeature(label)

    def registerCategoricalFeature(
        self, label: str, possible_values: List[Any]
    ) -> None:
        self.__feature_definitions[label] = CategoricalFeature(label, possible_values)

    def createEmptyWeightVector(self) -> WeightVector:
        return WeightVector(self.__feature_definitions)

    def getFeatureValues(self, label: str) -> List[Any]:
        if label not in self.__feature_definitions:
            raise Exception("Attempting to get values of feature not yet registered...")

        return self.__feature_definitions[label].possible_values
