from unittest import loader
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
import requests
from bs4 import BeautifulSoup
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Number
from django.shortcuts import render, get_object_or_404

# récupérer le contenu HTML de la page Jumia en fonction des paramètres
def get_html_content(nomSmart,prixMax,page):
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE

    if(nomSmart is None and prixMax is None) or (nomSmart is None and prixMax ==''):
        if (page == 1):
            html_content = session.get(
            f'https://www.jumia.com.tn/catalog/?q=smartphone',
            headers=session.headers).text
        else:
            html_content = session.get(
            f'https://www.jumia.com.tn/catalog/?q=smartphone&page={page}#catalog-listing',
            headers=session.headers).text  


    if  nomSmart == '' and prixMax !='':
            html_content = session.get(
            f'https://www.jumia.com.tn/catalog/?q=smartphone&price=4-{prixMax}#catalog-listing',
            headers=session.headers).text
    if(prixMax is None and nomSmart is not None):
        nomSmart=nomSmart.replace(' ', '-')
        html_content = session.get(
        f'https://www.jumia.com.tn/{nomSmart}/?q=smartphone#catalog-listing',
        headers=session.headers).text
    if(nomSmart is not None and prixMax is not None):
        nomSmart=nomSmart.replace(' ', '-')    
        html_content = session.get(
        f'https://www.jumia.com.tn/{nomSmart}/?q=smartphone&price=4-{prixMax}#catalog-listing',
        headers=session.headers).text
    if(nomSmart=='' and prixMax==''):
        html_content = session.get(
        f'https://www.jumia.com.tn/catalog/?q=smartphone',
        headers=session.headers).text                 
    return html_content

# gèrer la requête POST
def filter(request):
    nomS=request.POST.get('nomSmart')
    print(nomS)
    prixM=request.POST.get('prixMax')
    print(prixM)
    #pour verifier si il'ya pagination ou non
    ok=True
    #liste des articles
    articles = [] 
    text_list=[]
    #numero du page a partir de la requete GET
    page=request.GET.get('page')

    # objet nulber recuperer à partit de la base de données
    numbers = Number.objects.all()

    #liste des marques
    data_marques=[]

    if nomS is not None or prixM is not None:
        ok = False
       
    #contenu HTML de la page Jumia est récupéré    
    html_content=get_html_content(nomS,prixM,page)

    #extraire le contenu de la page HTML
    soup=BeautifulSoup(html_content,'html.parser')
    
    
    data_marques=soup.find_all("div", {"class": "-phs -pvxs -df -d-co -h-168 -oya -sc"})
    
    for m in data_marques:
        m_name=m.find_all("a", {"class": "fk-cb -me-start -fsh0"})
        text_list = [item.get_text() for item in m_name]
    
    articles=soup.find_all("article", {"class": "prd _fb col c-prd"})    
    
    data_name=[]
    data_price=[]
    data_remise=[]
    data_link=[]
    data_marque=[]
    data_pour=[]
    data_img=[]
    for art in articles:
        art_name=art.h3.text.replace('-', ' ')
        art_link=art.a['href']
        art_img=art.img['data-src']
        
        if(art.find("div", {"class": "s-prc-w"}) is  None):
            art_price=art.find("div", {"class": "prc"}).text
            art_pour=None
            price_remise=None

        else :
            ch=art.find("div", {"class": "s-prc-w"}).text
            art_price=ch.split('D',1)[0]+'D'
            art_pour=ch.split('D',1)[1]
            price_remise =art.find("div", {"class": "prc"}).text


        art_marque=art.a['data-brand']
        data_pour.append(art_pour)
        data_name.append(art_name)
        data_link.append('https://www.jumia.com.tn/'+art_link)
        data_remise.append(price_remise)
        data_price.append(art_price)
        data_marque.append(art_marque)    
        data_img.append(art_img)
    
    #Les données des smartphones  mises en forme dans un objet DataFrame  pandas 
    art_data=pd.DataFrame({"nom" :data_name ,"image":data_img,"marque":data_marque ,"prix":data_price ,"pour":data_pour,"remise": data_remise, "lien" :data_link})
    
    #charge template form.html
    template=loader.get_template('form.html')
    context={
        'data':art_data.to_dict('records'),
        'marque':text_list,
        'numbers':numbers,
        'ok':ok,
        'nomSmart': nomS,
        'prixMax': prixM
    }   
    return HttpResponse(template.render(context,request))
