from typing import List, Any, Dict, Tuple, Optional
from abc import abstractmethod

from numpy import isin


class FeatureDefinition:
    def __init__(self, label: str) -> None:
        self.__label: str = label

    @property
    def label(self) -> str:
        return self.__label

    @abstractmethod
    def getParameters(self) -> Dict[str, Any]:
        return {}

    @abstractmethod
    def createPossibleFeatures(self) -> List[str]:
        return []

    @abstractmethod
    def registerFeatureWeights(
        self, value: Optional[Any], weight: float, bias: float
    ) -> None:
        pass

    @abstractmethod
    def calculateValue(self, value: Any) -> float:
        return 0


class ScalarFeature(FeatureDefinition):
    def __init__(self, label: str) -> None:
        super().__init__(label)
        self.__weight: float = 0
        self.__bias: float = 0

    def getParameters(
        self,
    ) -> Dict[str, Any]:
        return {
            f"{self.label}_weight": self.__weight,
            f"{self.label}_bias": self.__bias,
        }

    def createPossibleFeatures(self) -> List[str]:
        return [self.label]

    def registerFeatureWeights(
        self, value: Optional[Any], weight: float, bias: float
    ) -> None:
        if value is not None:
            raise Exception("Registering feature weights on value for scalar feature")

        self.__weight = weight
        self.__bias = bias

    def calculateValue(self, value: Any) -> float:
        return self.__weight * value + self.__bias


class CategoricalFeature(FeatureDefinition):
    def __init__(
        self, label: str, possible_values: List[Any], nullable: bool = False
    ) -> None:
        super().__init__(label)
        self.__values: List[Any] = possible_values
        self.__nullable = nullable
        self.__weights: Dict[Any, Tuple[float, float]] = {}

    def getParameters(self) -> Dict[str, Any]:
        vector = {}

        for possible_value in self.__values:
            vector[f"{self.label}_{possible_value}_weight"] = self.__weights[
                possible_value
            ][0]
            vector[f"{self.label}_{possible_value}_bias"] = self.__weights[
                possible_value
            ][1]

        return vector

    def registerFeatureWeights(
        self, value: Optional[Any], weight: float, bias: float
    ) -> None:
        if value is None:
            raise Exception(
                "Attempting to register feature weights on categorical feature with 'None' value"
            )

        if value not in self.__values:
            print(self.__values)
            raise Exception(
                f"Attempting to register feature weights on categorical feature with unavailable value: {value}"
            )

        self.__weights[value] = (weight, bias)

    def calculateValue(self, value: Any) -> float:
        return 1 * self.__weights[value][0] + self.__weights[value][1]


class ContextManager:
    def __init__(self) -> None:
        self.__feature_definitions: Dict[str, FeatureDefinition] = {}

    @property
    def feature_labels(self) -> List[str]:
        return list(self.__feature_definitions.keys())

    def registerScalarFeature(self, label: str) -> None:
        self.__feature_definitions[label] = ScalarFeature(label)

    def registerCategoricalFeature(
        self, label: str, possible_values: List[Any], nullable: bool
    ) -> None:
        self.__feature_definitions[label] = CategoricalFeature(
            label, possible_values, nullable
        )

    def registerScalarFeatureWeights(
        self, label: str, weight: float, bias: float
    ) -> None:
        if label not in self.__feature_definitions:
            raise Exception("Registering weights for feature not registered...")

        if not isinstance(self.__feature_definitions[label], ScalarFeature):
            raise Exception("Attempting to register weights on non scalar feature")

        self.__feature_definitions[label].registerFeatureWeights(None, weight, bias)

    def registerCategorialFeatureWeights(
        self, label: str, value: Any, weight: float, bias: float
    ) -> None:
        if label not in self.__feature_definitions:
            raise Exception(
                "Attempting to register weights for feature not registered..."
            )

        if not isinstance(self.__feature_definitions[label], CategoricalFeature):
            raise Exception("Attempting to register weights on non categorical feature")

        self.__feature_definitions[label].registerFeatureWeights(value, weight, bias)

    def get_expanded_features_and_weights(self) -> Dict[str, float]:
        features = {}

        for _, defintion in self.__feature_definitions.items():
            features.update(defintion.getParameters())

        return features

    def calculate_salience(self, features_values: Dict[str, Any]) -> float:
        for label in features_values.keys():
            if label not in self.__feature_definitions:
                raise Exception(
                    "Attempting Calculating salience with feature not registered"
                )

        for label in self.__feature_definitions.keys():
            if label not in self.feature_labels:
                raise Exception(
                    "Attempting Calculating salience with missing feature value"
                )

        sum = 0
        for label, feature_defintion in self.__feature_definitions.items():
            sum += feature_defintion.calculateValue(features_values[label])

        return sum
