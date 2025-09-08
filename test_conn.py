# Bestand: test_connection.py
from fabric import Connection
from getpass import getpass

# --- VUL HIER JE GEGEVENS IN ---
HOST = "35.214.223.10"
GEBRUIKER = "admin"
COMMANDO = "system log list" # Een simpel commando om te testen
# -----------------------------

try:
    wachtwoord = getpass(f"Voer wachtwoord in voor {GEBRUIKER}@{HOST}: ")

    print("\nVerbinding wordt gemaakt...")
    
    # Maak verbinding met de host
    # We voegen extra parameters toe om alleen wachtwoord-authenticatie te proberen
    with Connection(
        host=HOST,
        user=GEBRUIKER,
        connect_kwargs={
            "password": wachtwoord,
            "look_for_keys": False,    # Zoek niet naar SSH sleutels
            "allow_agent": False,      # Gebruik geen SSH agent
        },
    ) as c:
        print(f"Verbonden met {c.host}!")
        
        print(f"Commando uitvoeren: '{COMMANDO}'")
        result = c.run(COMMANDO, hide=True)
        
        print("\n--- RESULTAAT ---")
        print(result.stdout)
        print("-------------------\n")

except Exception as e:
    print("\n--- FOUT OPGETREDEN ---")
    import traceback
    traceback.print_exc() # Dit print de volledige, gedetailleerde fout
    print("-----------------------\n")