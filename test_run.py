from llm_conversation.conversation_manager import ConversationManager
from llm_conversation.ai_agent import AIAgent

# 1. Zwei verschiedene Charaktere erstellen
professor = AIAgent(
    name="Professor", 
    model="llama3:8b", 
    system_prompt="Du bist ein erfahrener Professor für Informatik. Du bist kritisch, aber fördernd.",
    temperature=0.7,
    ctx_size=4096
)

student = AIAgent(
    name="Student", 
    model="llama3:8b", 
    system_prompt="Du bist ein motivierter Student, der gerade seine Masterarbeit schreibt. Du stellst viele Fragen.",
    temperature=0.8, # Etwas kreativer
    ctx_size=4096
)

# 2. Den Manager mit BEIDEN Agenten starten
# Wir entfernen das 'break' im Loop, damit sie hin und her reden
conv = ConversationManager(
    agents=[professor, student], 
    initial_message="Professor, können Sie mir erklären, warum Multi-Agenten-Systeme für die Forschung so wichtig sind?"
)

print("\n--- Start der Live-Diskussion ---")

# Wir lassen die ersten 4 Runden laufen
runde = 0
for agent_name, response_iter in conv.run_conversation():
    print(f"\n[{agent_name} spricht]:")
    
    # Text "streamen" (Wort für Wort anzeigen für das Interaktions-Gefühl)
    full_text = ""
    for chunk in response_iter:
        print(chunk[len(full_text):], end="", flush=True)
        full_text = chunk
    print() # Zeilenumbruch nach der Nachricht

    runde += 1
    if runde >= 4: # Nach 4 Nachrichten stoppen wir
        break 

print("\n--- Simulation beendet ---")