import requests
import sys
import random
import os
import base64
import hashlib
import hmac
import json
from requests_oauthlib import OAuth1
from auth import tt_bearer_token, tt_consumer_api_key, tt_consumer_api_pass, \
    tt_access_token, tt_access_token_secret, img_client_id, img_client_secret

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
tt_auth_consumer = OAuth1(tt_consumer_api_key, tt_consumer_api_pass, tt_access_token, tt_access_token_secret)
tt_auth_bearer = f'Bearer {tt_bearer_token}'
img_auth = {'Authorization' : f'Client-ID {img_client_id}'}

class Bot():

    __dog = ('dogs',
             'corgi',
             'wigglebutts',
             'dogswithjobs',
             'blop',
             'whatswrongwithyourdog',
             'puppysmiles',
             'dogshowerthoughts')

    __cat = ('blep',
             'CatsStandingUp',
             'JellyBeanToes',
             'kittens',
             'CatsInBusinessAttire',
             'CatsonGlass',
             'CatsInSinks',
             'CatLoaf',
             'Cats')

    def __init__(self, user_id=None):
        self.__user_id = user_id
        self.twt = self.Twitter(self.__user_id)
        self.img = self.Imgur()

    def dog(self):
        dog_link = self.img.get_imglink(self.__dog)

        img = requests.get(dog_link)

        with open(os.path.join(THIS_FOLDER, 'temp/dog.png'), 'wb') as f:
            f.write(img.content)

        self.twt.manda_dm(media='dog.png')

    def cat(self):
        cat_link = self.img.get_imglink(self.__cat)

        img = requests.get(cat_link)

        with open(os.path.join(THIS_FOLDER, 'temp/cat.png'), 'wb') as f:
            f.write(img.content)

        self.twt.manda_dm(media='cat.png')

    def dm(self, msg):
        self.twt.manda_dm(msg)

    class Imgur():
        __gallery_endpoint = 'https://api.imgur.com/3/gallery/r/'

        #pega uma img aleatória pelo link,
        #o subject é um tuple com vários subreddits de um determinado assunto
        def get_imglink(self, subject):
            sort = 'time'
            window = 'week'
            page = 0

            rand_sub = random.randrange(0, 8)
            r = requests.get(f"{self.__gallery_endpoint}{subject[rand_sub]}/{sort}/{window}/{page}", headers=img_auth)
            data = r.json()

            rand_link = random.randrange(1, 101)
            img_link = data['data'][rand_link]['link']

            return img_link

    class Twitter():
        #os endpoints usados pelo bot
        __upload_endpoint = 'https://upload.twitter.com/1.1/media/upload.json'
        __dm_endpoint = 'https://api.twitter.com/1.1/direct_messages/events/new.json'
        __auth_test_endpoint = 'https://api.twitter.com/1.1/account/verify_credentials.json'

        #o id de quem vai receber a dm
        def __init__(self, reciever_id = None):
            self.__reciever_id = reciever_id

        def upload_img(self, media):

            #Declara o caminho da img e busca o tamanho dela em bytes
            file = os.path.join(THIS_FOLDER, f'temp/{media}')
            total_bytes = os.path.getsize(file)

            #inicia o processo de upload;
            # a função retorna o media_id fornecido pelo twitter
            media_id = self.upload_init(total_bytes)

            #esta função faz o upload em chunks de 5mb
            self.upload_append(file, media_id, total_bytes)

            #fecha o processo, agr o media_id pode ser utilizado
            # para mandar dms ou postar tweets
            self.upload_finalize(media_id)

            return media_id

        def upload_init(self, total_bytes):

            #Faz o request com o comando INIT, o media_category é para dms
            r_init = {'command': 'INIT',
                           'total_bytes': total_bytes,
                           'media_type': 'image/png',
                           'media_category': 'dm_image'}

            r = requests.post(self.__upload_endpoint, params=r_init, auth=tt_auth_consumer)

            #Esse print é para debug
            print(r.json())

            #Se não houver media_id no retorno ocorreu algo de errado,
            #presumidamente foi uma tentativa com um arquivo corrompido
            #ou que não seja uma img
            if 'media_id_string' not in r.json():
                self.manda_dm(self.__reciever_id, 'Opa patrão, catei um link zikado, '
                                             'faça seu pedido novamente nmrlzinha')

            self.check_request(r)

            return r.json()['media_id_string']

        def upload_append(self, file, media_id, total_bytes):

            #declara bytes_sent e segment_id e abre a img em modo 'read binary
            #segment_id = quantos chunks de 5mb foram uploaded
            segment_id = 0
            bytes_sent = 0

            f = open(file, 'rb')

            #Repete este loop enquanto não enviar o arquivo inteiro
            while bytes_sent < total_bytes:
                #aparemente 4*1024*1024 bytes dá 5mb... vivendo e aprendendo, vivendo e aprendendo
                chunk = f.read(4*1024*1024)

                #faz o request com o commando 'APPEND'
                r_append = {'command': 'APPEND',
                                 'media_id': media_id,
                                 'segment_index': segment_id}

                files = {'media': chunk}

                r = requests.post(self.__upload_endpoint, params=r_append, files=files, auth=tt_auth_consumer)

                #checa se a request deu certo
                self.check_request(r)

                #incrementa o segment_id e guarda quantos byte já mandou
                segment_id = segment_id + 1
                bytes_sent = f.tell()

            #fecha o arquivo ;)
            f.close()

        def upload_finalize(self, media_id):

            #aqui vc basicamente apenas checa com o twitter pra ver se deu tudo certo
            r_finalize = {'command': 'FINALIZE', 'media_id': media_id, }

            r = requests.post(self.__upload_endpoint, params=r_finalize, auth=tt_auth_consumer)

            self.check_request(r)

        def check_request(self, r):
            if r.status_code < 200 or r.status_code > 299:
                print(r.status_code)
                print(r.text)
                sys.exit(0)

        def manda_dm(self, msg=None, media=None):

            media_id = ''
            r_dm = {}

            #se tiver houver media o upload é feito e
            #a estrutura do pedido é feita corretamente
            if (media != None):
                media_id = self.upload_img(media)

                r_dm = {'event':
                            {'type': 'message_create',
                             'message_create': {'target': {'recipient_id': self.__reciever_id},
                                                'message_data': {
                                                'text': msg,
                                                'attachment': {'type': 'media', 'media': {'id': media_id}}}}}}
            else:
                r_dm = {'event':
                            {'type': 'message_create',
                             'message_create': {'target': {'recipient_id': self.__reciever_id},
                                                'message_data': {
                                                'text': msg, }}}}

            r = requests.post(self.__dm_endpoint, json=r_dm, auth=tt_auth_consumer)

        def crc_challenge(self, crc_token):
            #o teste crc que o twitter manda a cada 24 horas

            consumer_secret_bytes = tt_consumer_api_pass.encode('utf-8')
            crc_token_bytes = crc_token.encode('utf-8')
            sha256_hash_digest = hmac.new(consumer_secret_bytes, crc_token_bytes, hashlib.sha256).digest()

            r = {
                'response_token': f'sha256={base64.b64encode(sha256_hash_digest).decode()}'
            }

            return json.dumps(r)
