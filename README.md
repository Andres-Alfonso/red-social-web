## Crear maquina virtual
 - python -m venv env

    ### Iniciar maquina virtual
    - .\env\Scripts\activate
    
    ### instalar dependencias
    - pip install -r requirements.txt
    ## Si se instalan nuevas  dependencias con pip usar:
    - pip freeze > requirements.txt  ---> esto actualiza en archivo requirements.txt

## Migraciones
- python manage.py makemigrations
- python manage.py migrate

## iniciar servidor
python manage.py runserver
