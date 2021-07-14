# ScrappingPdfHtml

# Instalación

Con pip

`pip install -r requirements.txt`

Con poetry (recomendado)

`poetry install`

# Uso

De ahora en adelante usaremos `command` para referirnos al comando principal.

Con poetry `command` seria:

`poetry run main`

Si instalo directamente con pip o inicio un virtualenv, inicie el virtualenv, y ejecute:

`python3 path_to_src`

# Argumentos

Los argumentos disponibles son `path` y `search`.

El valor de `path` es la ubicación de los archivos html y pdf, es opcional y por defecto esta ubicado en la raiz de proyecto en el directorio assets.

```
root:
    assets:
        ...
    src:
        __main__.py
```

Se puede abreviar como `p`, y se puede utilizar de esta forma:

```
command --path './archivos'

command --path /home/user/docs

command -p '/home/user/archivos descargados/pdf'
```

El valor de `search` es la busqueda por nombre, es obligatorio. Se puede abreviar como `s`, y se puede utilizar de esta forma:

```
command --search PRESIDENTA

command --search 'Xavier Méndez'

command -s PRESIDENTA
```

El argumento `search` buscara todas las coincidencias del formato `SEÑOR[A]? {search}.-`, el argumento se busca tal cual, por lo que escribir **PRESIDENTA**, dara diferentes resultados si se busca **Presidenta**, **PresidenTa** o **PRESIDENTA (Ivone)**.
