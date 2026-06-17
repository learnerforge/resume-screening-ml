from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Settings:
    project_root: Path = Path(__file__).resolve().parents[1]
    skill_file: Path = field(init=False)

    spacy_model: str = "en_core_web_sm"
    sentence_transformer_model: str = "all-MiniLM-L6-v2"
    use_semantic: bool = False

    default_text_weight: float = 0.7
    default_skill_weight: float = 0.3
    default_experience_weight: float = 0.0

    max_upload_size_mb: int = 10

    log_level: str = "INFO"
    log_format: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    def __post_init__(self) -> None:
        self.skill_file = self.project_root / "resume_matcher" / "data" / "skills.txt"
        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        prefix = "RESUME_MATCHER_"
        for field_name in self.__dataclass_fields__:
            env_key = prefix + field_name.upper()
            env_val = os.environ.get(env_key)
            if env_val is not None:
                field_type = self.__dataclass_fields__[field_name].type
                if field_type is bool:
                    setattr(self, field_name, env_val.lower() in ("1", "true", "yes"))
                elif field_type is int:
                    setattr(self, field_name, int(env_val))
                elif field_type is float:
                    setattr(self, field_name, float(env_val))
                else:
                    setattr(self, field_name, env_val)


settings = Settings()
