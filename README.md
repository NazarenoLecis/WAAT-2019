# WAAT-2019
Repository del Corso WAAT AA-2018-19

## Setup NLTK


1. Aprire la console di Python e digitare i seguenti comandi:
    
    ```python
    
        import nltk
        print(nltk.__version__) # per verificare la versione
        nltk.download() # o nltk.download_gui() in caso di errore
    ```

2. Scaricare la collection _book_ dalla GUI, in caso non si riesca a visualizzare la GUI scaricare direttamente 
la collection con il seguente comando:

    ```python
    
        import nltk
        nltk.download('book') 
    ```
    
## Esercizio 1

Utilizzare i testi di Grazia Deledda e Luigi Pirandello per confrontare la _concordance_ e la _similarity_
della parola *donna*. I testi si trovano nella cartella _corpora_.

## Esercizio 2

Utilizzare i testi di Grazia Deledda e Luigi Pirandello per confrontare la 30 parole, di lunghezza maggiore a 4, più comunemente 
utilizzate dai due autori.

## Esercizio 3

Creare un corpus ad hoc coi i testi dei due autori italiani suddivisi per categoria. Utilizzare questo
corspus per ottenete una distribuzione di frequenza condizionale per esaminare le differenze nelle lunghezze 
delle parole per autore.
