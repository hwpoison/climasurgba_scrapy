
# climasurgba_scrapy
Script para extraer imágenes infrarrojos del satélite GOES-16 del territorio argentino proporcionadas por la web https://climasurgba.com.ar/.
Se puede usar por linea de comandos.

Uso:
 - **python get_goes.py --help**  : obtener ayuda.
 - **python get_goes.py -t**  : obtener las imagenes disponibles hasta el momento del día y luego se crea una animación con ellas.
   
    **python get_goes.py -a [Nombre carpeta]** : crear una animación con
   las imagenes de una carpeta, admite varias a la vez separadas por una coma para poder animar mas de un día, por ejemplo: --animate 2021-02-01,2021-02-02
   
   **python get_goes.py -d AÑO/MES/DÍA** : descargar las imagenes disponibles de un día en especifico (El sitio climasurgba guarda
   hasta 5 meses).
   
    **python get_goes.py -m [numero mes]** : descarga todas las imagenes
   de un mes completo y luego crea una animación con ellas

    **python get_goes.py -q [calidad 1-10]** : Calidad de la animación final.

    **python get_goes.py -c [provincia ex: cordoba]** : Recortar una zona en especifico.

El script en sí puede ser modificado, contiene dos pequeñas clases que administran descargas multi-hilos, podría haber recurrido a la clase ThreadPoolExecutor pero no recuerdo por que limitación no podía encuadrarla así que me fué mas practico escribir una clase propia que se encargue de la gestión de hilos y descarga.

Un problema que puede surgir es que el sitio bloquee las solicitudes al servidor provocando multiples errores, que puede ser mitigado estableciendo un maximo de descargas simultaneas y algun temporizador de por medio. De todas formas si surge algun problemade conexión, el script tiene la capacidad de "volver a retomar la descarga" omitiendo los archivos que ya fueron descargados pudiendo intentar más tarde en caso de que el sitio no responda por un tiempo.

