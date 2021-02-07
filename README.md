# climasurgba_scrapy
Script para extraer imágenes infrarrojos del satélite GOES-16 del territorio argentino proporcionadas por la web https://climasurgba.com.ar/.
Se puede usar por linea de comandos.
Uso:
- **python get_goes.py -t **: obtener las imagenes disponibles hasta el momento del día y luego se crea una animación con ellas.
- **python get_goes.py -a [Nombre carpeta]** : crear una animación con las imagenes en la carpeta.
** python get_goes.py -d AÑO/MES/DÍA** : descargar las imagenes disponibles de un día en especifico (El sitio climasurgba guarda hasta 5 meses).
- **python get_goes.py -m [numero mes]** : descarga todas las imagenes de un mes completo y luego crea una animación con ellas

El script en sí puede ser modificado, contiene dos pequeñas clases que administran descargas multi-hilos, podría haber recurrido a la clase ThreadPoolExecutor pero no recuerdo por que limitación no podía encuadrarla así que me fué mas practico escribir una clase propia que se encargue de la gestión de hilos y descarga.

Un problema que puede surgir es que el sitio bloquee las solicitudes al servidor provocando multiples errores, que puede ser mitigado estableciendo un maximo de descargas simultaneas y algun temporizador de por medio. De todas formas si surge algun problemade conexión, el script tiene la capacidad de "volver a retomar la descarga" omitiendo los archivos que ya fueron descargados.
