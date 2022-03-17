from typing import List, Any, Dict, Tuple
from abc import abstractmethod


class FeatureDefinition:
    def __init__(self, label: str) -> None:
        self.__label: str = label

    @property
    def label(self) -> str:
        return self.__label

    @abstractmethod
    def createVector(self, value: Any) -> Dict[str, Any]:
        return {}

    @abstractmethod
    def createPossibleFeatures(self) -> List[str]:
        return []


class ScalarFeature(FeatureDefinition):
    def __init__(self, label: str) -> None:
        super().__init__(label)

    def createVector(self, value: Any) -> Dict[str, Any]:
        return {f"{self.label}": value}

    def createPossibleFeatures(self) -> List[str]:
        return [self.label]


class CategoricalFeature(FeatureDefinition):
    def __init__(
        self, label: str, possible_values: List[Any], nullable: bool = False
    ) -> None:
        super().__init__(label)
        self.__values: List[Any] = possible_values
        self.__nullable = nullable

    def createVector(self, value: Any) -> Dict[str, Any]:
        vector = {}

        if value not in self.__values and (value is None and self.__nullable):
            raise Exception(
                "Creating Categorical Feature with value that was not registered..."
            )

        for possible_value in self.__values:
            vector[f"{self.label}_{possible_value}"] = (
                1 if possible_value == value else 0
            )

        return vector

    def createPossibleFeatures(self) -> List[str]:
        features = []

        for possible_value in self.__values:
            features.append(f"{self.label}_{possible_value}")

        return features


class ContextManager:
    def __init__(self) -> None:
        self.__feature_definitions: Dict[str, FeatureDefinition] = {}

    def registerScalarFeature(self, label: str) -> None:
        self.__feature_definitions[label] = ScalarFeature(label)

    def registerCategoricalFeature(
        self, label: str, possible_values: List[Any], nullable: bool
    ) -> None:
        self.__feature_definitions[label] = CategoricalFeature(
            label, possible_values, nullable
        )

    @property
    def feature_labels(self) -> List[str]:
        return list(self.__feature_definitions.keys())

    def create_feature_vector(self, values: Dict[str, Any]) -> Dict[str, float]:
        vector = {}

        for label, defintion in self.__feature_definitions.items():
            vector = vector | defintion.createVector(values[label])

        return vector

    def get_expanded_features(self) -> List[str]:
        vector = []

        for _, defintion in self.__feature_definitions.items():
            vector.extend(defintion.createPossibleFeatures())

        return vector
