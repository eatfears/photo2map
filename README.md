# photo2map

Converts photos from space to map projections.
Equirectangular, Mercator and Miller projections available

```
$ python photo2map.py -h
usage: photo2map.py [-h] [-R RADIUS] [-H HEIGHT] [-slon SAT_LONGITUDE]
                    [-i INPUT] [-o OUTPUT] [-w WIDTH] [-di] [-m {t,v,f}]
                    [-p {eq,mer,mil}] [-z ZOOM] [-lat LATITUDE]
                    [-lon LONGITUDE] [-f FOV] [-j THREADS]

optional arguments:
  -h, --help            show this help message and exit
  -R RADIUS, --radius RADIUS
                        Planet radius in kilometers (default 6371.0)
  -H HEIGHT, --height HEIGHT
                        Satellite height above surface (default 35786.0)
  -slon SAT_LONGITUDE, --sat-longitude SAT_LONGITUDE
                        Satellite longitude degrees (default 76.0)
  -i INPUT, --input INPUT
                        Input image filename (default input.jpg)
  -o OUTPUT, --output OUTPUT
                        Output image filename (default output.png)
  -w WIDTH, --width WIDTH
                        Output image width (default 1000)
  -di                   Do not use bilinear interpolation (default False)
  -m {t,v,f}, --mode {t,v,f}
                        Target, Visible or Full (experimental!) mode (default
                        t)
  -p {eq,mer,mil}, --projection {eq,mer,mil}
                        Projection (default mer)
  -z ZOOM, --zoom ZOOM  Image zoom factor (default 1.0)
  -lat LATITUDE, --latitude LATITUDE
                        Target latitude degrees (default 0.0)
  -lon LONGITUDE, --longitude LONGITUDE
                        Target longitude degrees (default satellite)
  -f FOV, --fov FOV     FOV of input image (default 17.89)
  -j THREADS, --threads THREADS
                        Multithreading (default 1)
```

<details> 
  <summary>Sample</summary>
  
  Input:
  
  ![input image](https://habrastorage.org/web/a71/1c2/a46/a711c2a469434e3fbc4f61525d8baa64.jpg)
  
  Output:
  
  ![output image](https://habrastorage.org/web/666/dfa/2d6/666dfa2d6d264947bd970c24196ce672.jpg)
  
  Input:
  
  ![input image](https://hsto.org/web/9da/981/13d/9da98113dddc46deb502da2e5430a4cb.jpg)
  
  Output:
  
  ![output image](https://hsto.org/web/e4a/1d7/f21/e4a1d7f21f0041678bfad0806f247830.jpg)
  
</details>
