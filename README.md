# Documentation
## Quick Start Guide
Steps on how to use the file with example code using the askervein.asc file and default.mpg0009 file provided in the repo.

1. The HillModel class takes an ESRI Ascii file as an input to create an instance.
```python
askervein = HillModel("askervein.asc")
```
2. Use the EA2XYZ method to convert the ESRI Ascii format to the XYZ file format.(Note: the EA2XYZ method is set to save by default, to prevent this "N" is passed to the save argument)
```python
askervein.EA2XYZ(save = "N")
```
3. Use the hill_map method to create contour plots of the elecation of the hill.
```python
askervein.hill_map(domain_length = 3200, domain_width = 4000, x_offset = 1060, y_offset = 3800, angle = 227)
```
4. Use the combo_map method to include the landing zones of particles from particle files using the ensight file format.
```python
askervein.combo_map("default.mpg0009")
```
5. Use the landing_bar method to plot the distribution of the particle landings downwind from the source of the particles. The x-coordinate of the source of the particles must be provided to the source argument.
```python
askervein.landing_bar("default.mpg0009", source = 1000)
```
6. Use the sum_line method to plot the cumulative sum of the particle landings downwind from the source.
```python
askervein.sum_line("default.mpg0009")
```
