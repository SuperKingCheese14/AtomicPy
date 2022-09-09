import json
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from utils import func_args_preprocessing

class AtomicAssetsAPI:

    __API_URL_BASE = 'https://wax.api.atomicassets.io/atomicassets/v1/'
    
    
    def __init__(self, api_key: str = '', retries=5):
        self.api_key = api_key
        
        self.api_base_url = self.__API_URL_BASE
        self.request_timeout = 120

        self.session = requests.Session()
        retries = Retry(total=retries, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
    
    def __request(self, url):
        # print(url)
        try:
            response = self.session.get(url, timeout=self.request_timeout)
        except requests.exceptions.RequestException:
            raise

        try:
            response.raise_for_status()
            content = json.loads(response.content.decode('utf-8'))
            return content
        except Exception as e:
            # check if json (with error message) is returned
            try:
                content = json.loads(response.content.decode('utf-8'))
                raise ValueError(content)
            # if no json
            except json.decoder.JSONDecodeError:
                pass

            raise
            
    def __api_url_params(self, api_url, params, api_url_has_params=False):

        if params:
            # if api_url contains already params and there is already a '?' avoid
            # adding second '?' (api_url += '&' if '?' in api_url else '?'); causes
            # issues with request parametes (usually for endpoints with required
            # arguments passed as parameters)
            api_url += '&' if api_url_has_params else '?'
            for key, value in params.items():
                if type(value) == bool:
                    value = str(value).lower()

                api_url += "{0}={1}&".format(key, value)
            api_url = api_url[:-1]
        return api_url
        
    # ---------- PING ----------#
    def ping(self, **kwargs):
        """Check API server status"""

        api_url = '{0}ping'.format(self.api_base_url)
        api_url = self.__api_url_params(api_url, kwargs)

        return self.__request(api_url)
            
    # ---------- GET THE NUMBER OF NFT'S OWNED BY AN ACCOUNT ACCORDING TO COLLECTION NAME ---------- #        
            
    @func_args_preprocessing
    def get_accounts(self, match_owner, collection_name, **kwargs):
        """Get the total number of NFT's owned by an account according to collection name"""

        kwargs['match_owner'] = match_owner
        kwargs['collection_name'] = collection_name

        api_url = '{0}accounts'.format(self.api_base_url)
        api_url = self.__api_url_params(api_url, kwargs)
        assets = self.__request(api_url)['data'][0]['assets']
        return assets
        
    # ---------- GET LIST OF COLLECTIONS OWNED BY AN ACCOUNT ---------- #
        
    @func_args_preprocessing
    def get_account_collections(self, account, **kwargs):
        """Get a list of collections owned by an account"""

        collection_response = requests.get('https://wax.api.atomicassets.io/atomicassets/v1/accounts/'+str(account))
        collection_data = collection_response.text
        parse_data = json.loads(collection_data)
        collections = parse_data['data']['collections']
        collections_list = []
        for collection in collections:
            collections_list.append(collection['collection']['collection_name'])
           
        return collections_list
        
        
    # ---------- GET ASSET ID's ---------- #
        
    @func_args_preprocessing
    def get_assets(self, **kwargs):
         """Get assets by collection name, schema name or template ID"""
         
         api_url = '{0}assets'.format(self.api_base_url)
         api_url = self.__api_url_params(api_url, kwargs)
         assets = self.__request(api_url)['data']
         asset_ids = []
         
         for ids in assets:
             asset_ids.append(ids['asset_id'])
         return asset_ids
         
    # ---------- GET ASSET BY ASSET ID ---------- #
    
    @func_args_preprocessing
    def get_asset_id(self, asset_id, **kwargs):
        """Fetch asset by ID"""
        
        kwargs['asset_id'] = asset_id
        api_url = '{0}assets'.format(self.api_base_url)
        api_url = self.__api_url_params(api_url, kwargs)
        asset = self.__request(api_url)['data']
        print(api_url)
        
        return asset
        
    # ---------- GET OWNER OF ASSET BY ASSET ID ---------- #
        
    @func_args_preprocessing
    def get_asset_owner(self, asset_id, **kwargs):
        """Fetch owner of asset by asset ID"""
        
        kwargs['asset_id'] = asset_id
        api_url = '{0}assets'.format(self.api_base_url)
        api_url = self.__api_url_params(api_url, kwargs)
        owner = self.__request(api_url)['data'][0]['owner']
        
        return owner
        
    # ---------- GET AUTHORIZED ACCOUNT(S) OF ASSET ---------- #
        
    @func_args_preprocessing
    def get_auth_accounts(self, asset_id, **kwargs):
        """Fetch authorized accounts of asset by asset ID"""
        
        kwargs['asset_id'] = asset_id
        api_url = '{0}assets'.format(self.api_base_url)
        api_url = self.__api_url_params(api_url, kwargs)
        auth_accounts = self.__request(api_url)['data'][0]['collection']['authorized_accounts']
        
        return auth_accounts
        
    # ---------- GET AUTHORIZED ACCOUTNS OF COLLECTION ---------- #
        
    @func_args_preprocessing
    def get_auth_accounts_col(self, collection_name, **kwargs):
        """Fetch authorized accounts of collection by collection name"""
        
        kwargs['collection_name'] = collection_name
        api_url = '{0}assets'.format(self.api_base_url)
        api_url = self.__api_url_params(api_url, kwargs)
        auth_accounts = self.__request(api_url)['data'][0]['collection']['authorized_accounts']
        
        return auth_accounts
        
    # ---------- GET TOTAL NUMBER OF ASSETS MINTED BY COLLECTION ---------- #
    
    @func_args_preprocessing
    def get_col_total_assets(self, collection_name, **kwargs):
        """Fetch the total number of minted NFT's by collection """
        
        asset_response = requests.get('https://wax.api.atomicassets.io/atomicassets/v1/collections/'+str(collection_name)+'/stats')
        
        data = asset_response.text
        
        parse_data = json.loads(data)
        
        total_assets = parse_data['data']['assets']
        
        return total_assets
        
    # ---------- GET TOTAL NUMBER OF ASSETS BURNED BY COLLECTION ---------- #
    
    @func_args_preprocessing
    def get_col_total_burned(self, collection_name, **kwargs):
        """Fetch the total number of burned NFT's by collection"""
    
        asset_response = requests.get('https://wax.api.atomicassets.io/atomicassets/v1/collections/'+str(collection_name)+'/stats')

        data = asset_response.text
        
        parse_data = json.loads(data)
        
        total_assets = parse_data['data']['burned']
        
        return total_assets
    
    
        

        

    
