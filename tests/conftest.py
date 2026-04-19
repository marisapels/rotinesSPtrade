from __future__ import annotations

import pandas as pd
import pytest

from tests.fixtures.bars import daily_bars


@pytest.fixture
def bars() -> pd.DataFrame:
    return daily_bars()
