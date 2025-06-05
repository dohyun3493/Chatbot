import sys
import os
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from chatbot import run_chat
from alerts import amr_alert
    
    
#Chatbot 실행 
if __name__ == "__main__":
    alert_thread = threading.Thread(target=amr_alert, daemon=True)
    #alert_thread.start()
    run_chat()