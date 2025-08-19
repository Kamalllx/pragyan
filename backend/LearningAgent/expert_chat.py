import os
import json
from dotenv import load_dotenv
from agent_coordinator import AgentCoordinator, LearningSession
import time
import re

# Load environment variables
load_dotenv()

class EducationalChat:
    def __init__(self):
        # Initialize the agent coordinator
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("Please set the GROQ_API_KEY in your .env file")
        
        self.coordinator = AgentCoordinator(groq_api_key=groq_api_key)
        self.active_session = None
        self.current_topic = None
        self.subtopics = []
        self.current_agent = None
        
    def print_styled(self, text, style="normal"):
        """Print text with some basic styling"""
        if style == "header":
            print(f"\n{'='*80}\n{text.center(80)}\n{'='*80}")
        elif style == "subheader":
            print(f"\n{'-'*80}\n{text.center(80)}\n{'-'*80}")
        elif style == "agent":
            print(f"\n🤖 {text}")
        elif style == "system":
            print(f"\n🔧 {text}")
        elif style == "user":
            print(f"\n👤 You: {text}")
        elif style == "thinking":
            print(f"\n💭 Thinking...", end="", flush=True)
        else:
            print(text)
    
    def show_welcome(self):
        """Display welcome message and instructions"""
        self.print_styled("EDUCATIONAL AGENT SYSTEM", "header")
        self.print_styled("Welcome to your interactive learning assistant!", "system")
        self.print_styled("You can chat with these specialized agents:", "system")
        self.print_styled("1. Concept Explorer - Breaks down topics into digestible chunks", "system")
        self.print_styled("2. Assessment Agent - Creates and grades personalized quizzes", "system")
        self.print_styled("3. Motivation Agent - Tracks engagement and provides encouragement", "system")
        self.print_styled("4. Resource Curator - Finds and recommends learning materials", "system")
        self.print_styled("5. Full Learning Session - Use all agents in sequence", "system")
        self.print_styled("\nCommands:", "system")
        self.print_styled("  /agent <number> - Switch to a specific agent", "system")
        self.print_styled("  /topic <topic> - Set or change your learning topic", "system")
        self.print_styled("  /session - Start a full learning session on your topic", "system")
        self.print_styled("  /help - Show these instructions", "system")
        self.print_styled("  /quit - Exit the chat", "system")
    
    def select_agent(self, agent_num):
        """Select an agent to interact with"""
        try:
            agent_num = int(agent_num)
            if agent_num == 1:
                self.current_agent = "concept_explorer"
                self.print_styled("Switched to Concept Explorer Agent", "system")
            elif agent_num == 2:
                self.current_agent = "assessment_agent"
                self.print_styled("Switched to Assessment Agent", "system")
            elif agent_num == 3:
                self.current_agent = "motivation_agent"
                self.print_styled("Switched to Motivation Agent", "system")
            elif agent_num == 4:
                self.current_agent = "resource_curator"
                self.print_styled("Switched to Resource Curator Agent", "system")
            elif agent_num == 5:
                self.current_agent = "full_session"
                self.print_styled("Ready to start a full learning session", "system")
            else:
                self.print_styled("Invalid agent number. Please choose 1-5.", "system")
        except ValueError:
            self.print_styled("Please enter a valid number.", "system")
    
    def set_topic(self, topic):
        """Set the current learning topic"""
        self.current_topic = topic
        self.print_styled(f"Topic set to: {topic}", "system")
        
        # If we already have an agent selected, we can ask for immediate feedback
        if self.current_agent == "concept_explorer":
            self.print_styled("Would you like me to break down this topic now? (yes/no)", "system")
        elif self.current_agent == "assessment_agent":
            self.print_styled("Would you like me to create a quiz on this topic now? (yes/no)", "system")
        elif self.current_agent == "resource_curator":
            self.print_styled("Would you like me to find learning resources on this topic now? (yes/no)", "system")
        elif self.current_agent == "full_session":
            self.print_styled("Ready to start a full learning session on this topic. Type /session to begin.", "system")
    
    def run_full_session(self):
        """Run a complete learning session on the current topic"""
        if not self.current_topic:
            self.print_styled("Please set a topic first using /topic <topic>", "system")
            return
        
        self.print_styled(f"Starting a full learning session on: {self.current_topic}", "subheader")
        
        # Step 1: Concept exploration
        self.print_styled("STEP 1: Breaking down the topic...", "system")
        self.print_styled("Concept Explorer is analyzing your topic...", "thinking")
        concept_result = self.coordinator.concept_explorer.run(
            f"Break down the topic '{self.current_topic}' into digestible subtopics. Provide 3-5 key subtopics with brief explanations."
        )
        print("\r" + " " * 80)  # Clear the thinking line
        self.print_styled("Concept Explorer", "agent")
        print(concept_result)
        
        # Try to extract subtopics from the response
        # This is a simple regex approach - in production you might want more robust parsing
        subtopic_match = re.findall(r'(?:Subtopic|Topic) ?\d?: ?([\w\s]+)', concept_result)
        if subtopic_match:
            self.subtopics = subtopic_match
            self.print_styled(f"Identified subtopics: {', '.join(self.subtopics)}", "system")
        
        # Step 2: Create a quiz
        self.print_styled("\nSTEP 2: Creating a personalized quiz...", "system")
        self.print_styled("Assessment Agent is creating your quiz...", "thinking")
        subtopics_text = ', '.join(self.subtopics) if self.subtopics else self.current_topic
        quiz_result = self.coordinator.assessment_agent.run(
            f"Create a quiz with 3 multiple-choice questions about '{self.current_topic}' focusing on: {subtopics_text}."
        )
        print("\r" + " " * 80)  # Clear the thinking line
        self.print_styled("Assessment Agent", "agent")
        print(quiz_result)
        
        # Step 3: Simulate quiz taking (in a real app, this would be interactive)
        self.print_styled("\nSTEP 3: Taking the quiz...", "system")
        self.print_styled("In a complete application, you would take the quiz here.", "system")
        self.print_styled("For demonstration, we'll simulate quiz results.", "system")
        
        # Sample quiz results (would come from user input in a real app)
        user_responses = [
            {"question_id": 1, "selected_answer": "B", "is_correct": True},
            {"question_id": 2, "selected_answer": "A", "is_correct": False},
            {"question_id": 3, "selected_answer": "C", "is_correct": True}
        ]
        
        # Step 4: Grade the quiz
        self.print_styled("\nSTEP 4: Grading your responses...", "system")
        self.print_styled("Assessment Agent is grading your quiz...", "thinking")
        grading_result = self.coordinator.assessment_agent.run(
            f"Grade these quiz responses: {json.dumps(user_responses)}"
        )
        print("\r" + " " * 80)  # Clear the thinking line
        self.print_styled("Assessment Agent", "agent")
        print(grading_result)
        
        # Extract score for motivation agent (simplified)
        score_match = re.search(r'(\d+)/(\d+)', grading_result)
        score = 0.67  # Default
        if score_match:
            correct = int(score_match.group(1))
            total = int(score_match.group(2))
            score = correct / total if total > 0 else 0
        
        # Step 5: Provide motivation
        self.print_styled("\nSTEP 5: Providing motivation and encouragement...", "system")
        self.print_styled("Motivation Agent is analyzing your performance...", "thinking")
        engagement_data = {
            "engagement_level": "high",
            "completion_rate": 1.0,
            "time_spent": 120,
            "recent_score": score
        }
        
        motivation_result = self.coordinator.motivation_agent.run(
            f"The user has been learning about {self.current_topic}. "
            f"Their engagement data is: {json.dumps(engagement_data)}. "
            f"Provide tailored encouragement."
        )
        print("\r" + " " * 80)  # Clear the thinking line
        self.print_styled("Motivation Agent", "agent")
        print(motivation_result)
        
        # Step 6: Recommend resources
        self.print_styled("\nSTEP 6: Finding learning resources...", "system")
        self.print_styled("Resource Curator is finding materials for you...", "thinking")
        
        # Find the subtopic with lowest score (simulated)
        weak_areas = [self.subtopics[1]] if self.subtopics else [self.current_topic]
        
        resource_result = self.coordinator.resource_curator.run(
            f"The user is learning about {self.current_topic} and needs help with: {', '.join(weak_areas)}. "
            f"Recommend 3 diverse learning resources (articles, videos, interactive tools)."
        )
        print("\r" + " " * 80)  # Clear the thinking line
        self.print_styled("Resource Curator", "agent")
        print(resource_result)
        
        self.print_styled("\nLearning session completed! You can continue chatting with any agent.", "system")
    
    def process_message(self, message):
        """Process user messages and commands"""
        # Handle commands
        if message.startswith('/'):
            if message.startswith('/agent '):
                agent_num = message[7:].strip()
                self.select_agent(agent_num)
                return
            
            elif message.startswith('/topic '):
                topic = message[7:].strip()
                self.set_topic(topic)
                return
            
            elif message == '/session':
                self.run_full_session()
                return
            
            elif message == '/help':
                self.show_welcome()
                return
            
            elif message == '/quit':
                self.print_styled("Thank you for using the Educational Agent System. Goodbye!", "system")
                return False
            
            else:
                self.print_styled("Unknown command. Type /help for available commands.", "system")
                return
        
        # Handle normal messages
        if not self.current_agent:
            self.print_styled("Please select an agent first using /agent <number>", "system")
            return
        
        # Process message with the current agent
        if self.current_agent == "full_session":
            self.print_styled("To start a full learning session, please use /session", "system")
        else:
            agent = getattr(self.coordinator, self.current_agent)
            self.print_styled("Thinking...", "thinking")
            response = agent.run(message)
            print("\r" + " " * 80)  # Clear the thinking line
            
            # Show which agent is responding
            agent_names = {
                "concept_explorer": "Concept Explorer",
                "assessment_agent": "Assessment Agent",
                "motivation_agent": "Motivation Agent",
                "resource_curator": "Resource Curator"
            }
            self.print_styled(agent_names[self.current_agent], "agent")
            print(response)
        
        return True
    
    def start(self):
        """Start the chat interface"""
        self.show_welcome()
        
        running = True
        while running:
            user_input = input("\n> ")
            self.print_styled(user_input, "user")
            result = self.process_message(user_input)
            if result is False:
                running = False

if __name__ == "__main__":
    chat = EducationalChat()
    chat.start()