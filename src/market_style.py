"""Map the supplied semantic tokens to Streamlit CSS and Plotly colours."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def theme_tokens(mode):
    source = (ROOT / "prospectlens-design-system/tokens.css").read_text(encoding="utf-8")
    body = re.search(r'\[data-theme="' + mode + r'"\]\s*\{([^}]+)\}', source).group(1)
    return dict(re.findall(r"--pl-([\w-]+)\s*:\s*([^;]+);", body))


def dashboard_css(mode):
    source = (ROOT / "prospectlens-design-system/tokens.css").read_text(encoding="utf-8")
    # Native Streamlit theme selection is the authority for both CSS and charts.
    override = ":root{" + "".join(f"--pl-{key}:{value};" for key, value in theme_tokens(mode).items()) + "}"
    return source + override + (ROOT / "assets/market.css").read_text(encoding="utf-8")
