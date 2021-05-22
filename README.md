# Quick Start Guide
1. The HillModel Class takes an ESRI Ascii file as an input to create an instance.
```python
askervein = HillModel("askervein.asc")
```

2. Use the EA2XYZ method to convert the ESRI Ascii format to the XYZ file format.
```python
askervein.EA2XYZ()
```

3. Use the hill_map method to create contour plots of the elecation of the hill.
```python
askervein.hill_map(domain_length=3200, domain_width=4000, x_offset=1060, y_offset=3800, angle=227)
```
