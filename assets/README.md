# Assets Directory

This directory contains static assets for the Kiwi AI application.

## Structure

- **svg/**: Scalable Vector Graphics for icons and illustrations.
- **img/**: Raster images (PNG, JPG, etc.).
- **css/**: Custom Stylesheets.

## Usage

To use an SVG in the application, you can read the file content:

```python
with open("assets/svg/icon.svg", "r") as f:
    svg_content = f.read()
st.markdown(svg_content, unsafe_allow_html=True)
```
