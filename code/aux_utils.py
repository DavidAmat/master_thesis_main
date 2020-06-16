import spotipy
from spotipy.oauth2 import SpotifyClientCredentials #To access authorised Spotify data

class spotify_utils:
    
    def __init__(self):
        # Spotify API credentials
        self.client_id = "348f94d3a73241188b2a89c91e1cfaee"
        self.client_secret = "b5b29b040ab843cf842cf4eb875caff1"
        
        
    def connect(self):
        client_credentials_manager = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API
        return sp


    # FUNCTIONS
    def levenshtein(self, s1, s2):
        """
        Function that implements roughly an approximation of the Levenshtein algorithm
        for string similarity. Is a distance metric, hence, the closer to 0, the most similar
        the strings will be
        """
        if len(s1) < len(s2):
            s1, s2 = s2, s1

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]/float(len(s1))