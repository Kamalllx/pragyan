import os
import json
import re
import string
from difflib import get_close_matches
from dotenv import load_dotenv
from agent_coordinator import AgentCoordinator
from utils.response_parser import extract_resources, extract_subtopics, extract_quiz_questions, serpapi_web_search

# Load environment variables
load_dotenv()

class SmartChat:
    """
    A seamless chat interface that automatically routes queries to appropriate
    agents without exposing the underlying agent structure to the user.
    """
    def __init__(self):
        # Initialize the agent coordinator
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("Please set the GROQ_API_KEY in your .env file")
        
        self.coordinator = AgentCoordinator(groq_api_key=groq_api_key)
        self.current_topic = None
        self.subtopics = []
        self.learning_context = {}
        self.quiz_in_progress = False
        self.current_quiz = None
        self.current_question_idx = 0
        self.quiz_responses = []
        
        # Common topics and their variations for fuzzy matching
        self.topic_variations = {
            "markov chain": ["markov", "makrov", "markof", "markof chain", "makrov chain", 
                             "markov chains", "makrov chains", "markov process"]
        }
        
    def print_styled(self, text, style="normal"):
        """Print text with some basic styling"""
        if style == "header":
            print(f"\n{'='*80}\n{text.center(80)}\n{'='*80}")
        elif style == "subheader":
            print(f"\n{'-'*80}\n{text.center(80)}\n{'-'*80}")
        elif style == "assistant":
            print(f"\n🧠 Assistant: {text}")
        elif style == "system":
            print(f"\n💡 {text}")
        elif style == "user":
            print(f"\n👤 You: {text}")
        elif style == "thinking":
            print(f"\n... thinking", end="", flush=True)
        elif style == "quiz":
            print(f"\n📝 {text}")
        else:
            print(text)
    
    def show_welcome(self):
        """Display welcome message and instructions"""
        self.print_styled("PERSONALIZED LEARNING ASSISTANT", "header")
        self.print_styled("Welcome! I'm your AI learning assistant. Just chat naturally with me about:", "system")
        self.print_styled("• Any topic you want to learn about", "system")
        self.print_styled("• Ask me to create a quiz on any subject", "system")
        self.print_styled("• Request learning resources or explanations", "system")
        self.print_styled("• Get motivation or learning strategies", "system")
        self.print_styled("\nYou can type 'help' for more information or 'quit' to exit.", "system")
        self.print_styled("\nLet's start learning! What topic are you interested in today?", "assistant")
    
    def _fuzzy_match_topic(self, text):
        """Match a potentially misspelled topic to known topics"""
        text = text.lower()
        
        # Check each known topic and its variations
        for main_topic, variations in self.topic_variations.items():
            for variation in variations:
                if variation in text:
                    return main_topic.title()
        
        # If no match in variations, try word-by-word similarity
        words = text.split()
        for main_topic in self.topic_variations.keys():
            topic_words = main_topic.split()
            for topic_word in topic_words:
                matches = get_close_matches(topic_word, words, n=1, cutoff=0.7)
                if matches:
                    return main_topic.title()
        
        return None
    
    def _detect_intent(self, message):
        """Determine the user's intent from their message"""
        message = message.lower()
        
        # Check for quiz intent with common misspellings
        quiz_words = ["quiz", "test", "question", "assessment", "exam"]
        give_words = ["give", "gime", "gimme", "get", "have", "take", "do", "create", "make", "start"]
        
        # First check direct quiz detection
        for quiz_word in quiz_words:
            if quiz_word in message:
                # Try to extract topic
                text_after_quiz = message.split(quiz_word, 1)[1] if quiz_word in message else message
                
                # Check for "on X", "about X" patterns
                topic_match = re.search(r'(?:on|about|for)\s+([^?.!]+)', text_after_quiz)
                if topic_match:
                    potential_topic = topic_match.group(1).strip()
                    # Try fuzzy matching first
                    matched_topic = self._fuzzy_match_topic(potential_topic)
                    if matched_topic:
                        self.current_topic = matched_topic
                    else:
                        self.current_topic = potential_topic.title()
                else:
                    # Check if there's any topic mention after the quiz word
                    if text_after_quiz.strip():
                        # Try fuzzy matching
                        matched_topic = self._fuzzy_match_topic(text_after_quiz)
                        if matched_topic:
                            self.current_topic = matched_topic
                
                return "quiz"
        
        # Check "give/gime/gimme me a quiz on X" pattern
        for give_word in give_words:
            if give_word in message and any(quiz in message for quiz in quiz_words):
                # Extract text after the give word
                full_text = message.split(give_word, 1)[1] if give_word in message else message
                
                # Try to find the topic
                for quiz_word in quiz_words:
                    if quiz_word in full_text:
                        text_after_quiz = full_text.split(quiz_word, 1)[1]
                        # Try fuzzy matching
                        matched_topic = self._fuzzy_match_topic(text_after_quiz)
                        if matched_topic:
                            self.current_topic = matched_topic
                            return "quiz"
                        
                        # If no fuzzy match, see if there's just a topic mentioned
                        if text_after_quiz.strip():
                            self.current_topic = text_after_quiz.strip().title()
                            return "quiz"
        
        # Handle other common intents
        if re.search(r'\b(quit|exit|bye|goodbye)\b', message) and len(message) < 20:
            return "quit"
            
        if re.search(r'\b(help|assist|command|instruction)\b', message) and len(message) < 20:
            return "help"
        
        if re.search(r'\b(resource|material|read|watch|article|video|book)\b', message):
            return "resources"
            
        if re.search(r'\b(learn|study|understand|topic|about)\s+(\w+\s*)+', message):
            topic_match = re.search(r'(learn|study|understand|topic|about)\s+([^?.!]+)', message)
            if topic_match:
                potential_topic = topic_match.group(2).strip()
                if len(potential_topic) > 2:  # Avoid setting very short topics
                    self.current_topic = potential_topic
                    return "set_topic"
                    
        if re.search(r'\b(comprehensive|full|complete|detailed|guide|overview|session)\b', message):
            return "learn_session"
            
        # Default to general query
        return "general_query"
    
    def _detect_query_type(self, query):
        """Determine which agent should handle this query"""
        query = query.lower()
        
        # Resource-related queries
        if re.search(r'(resource|material|learn|read|watch|article|video|course|book|tutorial)', query):
            return "resource"
            
        # Quiz/assessment-related queries
        elif re.search(r'(quiz|question|test|assess|exam|problem|exercise)', query):
            return "assessment"
            
        # Motivation-related queries
        elif re.search(r'(motivat|encourag|inspire|help me|stuck|difficult|hard|challenge|strategy)', query):
            return "motivation"
            
        # Concept-related queries (default if nothing else matches)
        elif re.search(r'(what is|how does|explain|understand|concept|topic|mean)', query):
            return "concept"
            
        # Default to concept explorer for general queries
        else:
            return "concept"
    
    def _get_formatted_resources(self, raw_response):
        """Extract and format resources from the agent response. If none, use web search."""
        resources = extract_resources(raw_response)
        used_fallback = False
        if not resources:
            # Fallback to real-time web search
            resources = serpapi_web_search(self.current_topic)
            used_fallback = True
            if not resources:
                return "I couldn't find specific resources. Please try a more specific query."
        formatted = "Here are some excellent resources on this topic:\n\n"
        for i, res in enumerate(resources, 1):
            title = res.get('title', f"Resource {i}")
            url = res.get('url', res.get('link', ''))
            desc = res.get('description', res.get('snippet', ''))
            # Guess type if not present
            res_type = res.get('type')
            if not res_type:
                if "youtube.com" in url:
                    res_type = "video"
                elif "wikipedia.org" in url:
                    res_type = "article"
                elif "course" in url or "coursera" in url or "edx.org" in url:
                    res_type = "course"
                else:
                    res_type = "resource"
            formatted += f"{i}. **{title}** ({res_type})\n"
            if desc:
                formatted += f"   {desc}\n"
            formatted += f"   {url}\n\n"
        if used_fallback:
            formatted += "\n(Results provided by real-time web search.)"
        return formatted
    
    def run_learning_session(self):
        """Run a complete learning session on the current topic"""
        if not self.current_topic:
            self.print_styled("I'd be happy to guide you through a learning session. What topic would you like to learn about?", "assistant")
            return
        
        self.print_styled(f"Great! Let's explore {self.current_topic} together. I'll break this down into manageable parts.", "assistant")
        
        # Step 1: Break down the topic
        self.print_styled("thinking...", "thinking")
        concept_result = self.coordinator.concept_explorer.run(
            f"Break down the topic '{self.current_topic}' into digestible subtopics. Provide 3-5 key subtopics with brief explanations."
        )
        print("\r" + " " * 80)  # Clear the thinking line
        
        # Parse and present subtopics in a clean format
        self.subtopics = extract_subtopics(concept_result)
        
        response = f"Here's how we can break down **{self.current_topic}**:\n\n"
        for i, subtopic in enumerate(self.subtopics, 1):
            if isinstance(subtopic, dict):
                name = subtopic.get('name', f"Subtopic {i}")
                explanation = subtopic.get('explanation', '')
                response += f"{i}. **{name}**\n   {explanation}\n\n"
            else:
                response += f"{i}. **{subtopic}**\n\n"
                
        self.print_styled(response, "assistant")
        
        # Step 2: Provide key resources
        self.print_styled("thinking...", "thinking")
        resource_result = self.coordinator.resource_curator.run(
            f"""Find 5 diverse, high-quality learning resources on '{self.current_topic}'.\nOnly include resources that are real and currently accessible on the web.\nDo NOT invent or hallucinate URLs—only include resources you are certain exist, and prefer well-known sites (Wikipedia, YouTube, Coursera, Khan Academy, etc).\nFor each resource, provide:\n- Title\n- Type (article, video, course, etc.)\n- The actual URL (no placeholders)\n- A brief description of what the learner will gain.\nFormat as a plain list."""
        )
        print("\r" + " " * 80)  # Clear the thinking line
        
        resources = self._get_formatted_resources(resource_result)
        self.print_styled(resources, "assistant")
        
        # Step 3: Offer a quiz or next steps
        self.print_styled("Would you like to test your knowledge with a quiz on this topic? Just say 'yes' or ask for a quiz when you're ready.", "assistant")
    
    # Replace the start_quiz method with this improved version

    # ... existing code ...

    def start_quiz(self):
        """Start an interactive quiz session"""
        if not self.current_topic:
            self.print_styled("I'd be happy to create a quiz for you. What topic would you like the quiz to be about?", "assistant")
            return

        self.print_styled(f"I'll create a quiz about {self.current_topic} for you.", "assistant")
        self.print_styled("thinking...", "thinking")

        # Improved prompt
        quiz_prompt = f"""Create a quiz with exactly 3 multiple-choice questions about {self.current_topic}.
    Each question must be in this format:
    Question X: [question text]?
    A. [option A]
    B. [option B]
    C. [option C]
    D. [option D]
    Correct answer: [A/B/C/D]

    No explanations, no extra text, no code blocks, no markdown, no numbering except as shown.
    """

        def parse_quiz(quiz_text):
            # Remove code blocks, markdown, and extra formatting
            quiz_text = re.sub(r'```[a-z]*\n?|\n```', '', quiz_text)
            quiz_text = re.sub(r'\*\*|\*', '', quiz_text)
            # Split into question blocks
            question_blocks = re.split(r'(?:^|\n)Question\s*\d+:', quiz_text)
            questions = []
            for block in question_blocks:
                block = block.strip()
                if not block or len(block) < 10:
                    continue
                # Extract question text
                q_match = re.match(r'([^\n\?]+\?)', block)
                question = q_match.group(1).strip() if q_match else block.split('\n')[0].strip()
                # Extract options
                options = []
                for letter in ['A', 'B', 'C', 'D']:
                    opt_match = re.search(rf'{letter}\.\s*([^\n]+)', block)
                    options.append(opt_match.group(1).strip() if opt_match else f"Option {letter}")
                # Extract answer
                ans_match = re.search(r'Correct answer:\s*([A-D])', block, re.IGNORECASE)
                answer = ans_match.group(1).upper() if ans_match else "A"
                questions.append({
                    "question": question,
                    "options": options,
                    "answer": answer
                })
            return questions

        try:
            quiz_result = str(self.coordinator.llm.invoke(quiz_prompt))
            print("\n[DEBUG] Raw quiz output:\n", quiz_result)  # <-- Add this for debugging
            questions = parse_quiz(quiz_result)
        except Exception as e:
            print("\r" + " " * 80)
            self.print_styled(f"Error generating quiz: {e}", "assistant")
            questions = []

        # Retry with a simpler prompt if parsing failed
        if not questions or len(questions) < 3:
            try:
                quiz_result = str(self.coordinator.llm.invoke(
                    f"Write 3 multiple choice questions about {self.current_topic}. Each question should have 4 options (A, B, C, D) and indicate the correct answer as 'Correct answer: X'."
                ))
                print("\n[DEBUG] Raw quiz output (retry):\n", quiz_result)
                questions = parse_quiz(quiz_result)
            except Exception:
                questions = []

        # Fallback to hardcoded quiz if still no questions
        if not questions or len(questions) < 3:
            if self.current_topic.lower() == "markov chain":
                questions = [
                    {
                        "question": "What is a Markov Chain?",
                        "options": [
                            "A sequence of random variables where future states depend only on the current state",
                            "A statistical model that always produces deterministic results",
                            "A type of neural network used for time series prediction",
                            "A mathematical structure that has no random elements"
                        ],
                        "answer": "A"
                    },
                    {
                        "question": "Which property is fundamental to Markov Chains?",
                        "options": [
                            "Complete dependence on all past states",
                            "Memorylessness (future depends only on present)",
                            "Deterministic state transitions",
                            "Continuous state space only"
                        ],
                        "answer": "B"
                    },
                    {
                        "question": "What is commonly used to represent a Markov Chain?",
                        "options": [
                            "Decision tree",
                            "Linked list",
                            "Transition matrix",
                            "Neural network"
                        ],
                        "answer": "C"
                    }
                ]
            else:
                self.print_styled("I'm having trouble creating a quiz right now. Let's try a different topic or approach.", "assistant")
                return

        self.current_quiz = questions[:3]
        self.quiz_in_progress = True
        self.current_question_idx = 0
        self.quiz_responses = []

        self.print_styled("Here's your quiz! Answer each question by typing the letter of your choice (A, B, C, or D).", "assistant")
        self.present_current_question()

# ... existing code ...w. Let's try a different topic or approach.", "assistant")
# Update the present_current_question method to better handle malformatted questions

# Update the present_current_question method

    def present_current_question(self):
        """Display the current quiz question"""
        if not self.quiz_in_progress or not self.current_quiz:
            return
        
        if self.current_question_idx >= len(self.current_quiz):
            self.finish_quiz()
            return
        
        question = self.current_quiz[self.current_question_idx]
        q_text = question.get("question", f"Question {self.current_question_idx + 1}")
        
        # Additional cleaning of question text
        q_text = re.sub(r'content=\'|\'$|additional_kwargs=\{\}|response_metadata=\{[^}]+\}', '', q_text)
        
        # Ensure the question is properly formatted and coherent
        if len(q_text.split()) <= 2 or not re.search(r'[a-zA-Z]{3,}', q_text):
            # This is a malformed question - fix it with a generic alternative
            if self.current_topic:
                topic_word = self.current_topic.split()[-1] if self.current_topic.split() else self.current_topic
                q_text = f"What is a key characteristic of {topic_word}?"
        
        # Ensure question ends with question mark
        if not q_text.endswith('?'):
            q_text += '?'
        
        # Clean option texts
        options = []
        raw_options = question.get("options", ["Option A", "Option B", "Option C", "Option D"])
        
        for opt in raw_options[:4]:
            # Clean metadata and fix formatting
            clean_opt = re.sub(r'content=\'|\'$|additional_kwargs=\{\}|response_metadata=\{[^}]+\}', '', str(opt))
            clean_opt = clean_opt.replace('\\n', ' ').replace('  ', ' ')
            options.append(clean_opt)
        
        # Ensure we have exactly 4 options
        while len(options) < 4:
            options.append(f"Option {len(options)+1}")
        
        # Format the question nicely
        display = f"Question {self.current_question_idx + 1}: {q_text}\n\n"
        for i, option in enumerate(options[:4]):
            letter = chr(65 + i)  # A, B, C, D
            display += f"{letter}. {option}\n"
        
        self.print_styled(display, "quiz")
    
    def process_quiz_answer(self, answer_text):
        """Process user's answer to current quiz question"""
        if not self.quiz_in_progress or not self.current_quiz:
            return False
        
        # Check for quiz exit intent
        if re.search(r'\b(stop|quit|exit|cancel)\b', answer_text.lower()):
            self.print_styled("Quiz canceled. You can start another quiz anytime by asking for one.", "assistant")
            self.quiz_in_progress = False
            self.current_quiz = None
            return True
        
        # Normalize the answer to uppercase single letter
        answer = answer_text.strip().upper()
        if len(answer) > 0:
            answer = answer[0]  # Take just the first character
        
        # Validate it's a legitimate answer (A, B, C, D)
        if answer not in "ABCD":
            self.print_styled("Please answer with A, B, C, or D only.", "assistant")
            return True
        
        # Record the response
        current_q = self.current_quiz[self.current_question_idx]
        correct_answer = current_q.get("answer", "A")
        is_correct = answer == correct_answer
        
        self.quiz_responses.append({
            "question_id": self.current_question_idx + 1,
            "question": current_q.get("question", ""),
            "selected_answer": answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })
        
        # Give immediate feedback
        if is_correct:
            self.print_styled("✅ Correct! Well done.", "assistant")
        else:
            self.print_styled(f"❌ Not quite. The correct answer is {correct_answer}.", "assistant")
        
        # Move to next question
        self.current_question_idx += 1
        
        # If we're done with all questions, finish the quiz
        if self.current_question_idx >= len(self.current_quiz):
            self.finish_quiz()
            return True
        
        # Otherwise, present the next question
        self.present_current_question()
        return True
    
    def finish_quiz(self):
        """Complete the quiz and provide results"""
        if not self.quiz_responses:
            return
        
        # Calculate score
        correct = sum(1 for resp in self.quiz_responses if resp.get("is_correct", False))
        total = len(self.quiz_responses)
        percentage = (correct / total) * 100 if total > 0 else 0
        
        # Format results
        result_text = f"Quiz Results: {correct}/{total} correct ({percentage:.1f}%)\n\n"
        for i, resp in enumerate(self.quiz_responses, 1):
            result_text += f"Q{i}: {'✓' if resp.get('is_correct') else '✗'} "
            result_text += f"You answered {resp.get('selected_answer')}, "
            result_text += f"Correct answer: {resp.get('correct_answer')}\n"
        
        self.print_styled(result_text, "quiz")
        
        # Get motivation message based on score
        self.print_styled("thinking...", "thinking")
        
        try:
            # Use direct LLM invocation for reliability
            prompt = f"The user just completed a quiz on {self.current_topic} and scored {percentage:.1f}%. "
            prompt += f"Provide a brief, encouraging message tailored to their performance."
            
            motivation = str(self.coordinator.llm.invoke(prompt))
            # Clean up response metadata
            motivation = re.sub(r'content=\'|\'$|additional_kwargs=\{\}|response_metadata=\{[^}]+\}', '', motivation)
            
            print("\r" + " " * 80)  # Clear the thinking line
            self.print_styled(motivation, "assistant")
        except Exception as e:
            print("\r" + " " * 80)  # Clear the thinking line
            self.print_styled("Thank you for completing the quiz! Keep learning and practicing to improve your knowledge.", "assistant")
        
        # Reset quiz state
        self.quiz_in_progress = False
        self.current_quiz = None
        self.quiz_responses = []
    
    def find_resources(self, message=None):
        """Find learning resources for the current topic (agent first, fallback to web search)."""
        # Try to extract topic from message if not set
        if not self.current_topic and message:
            topic_match = re.search(r'(?:about|on|for|of|in|to|for)\s+([^?.!]+)', message, re.IGNORECASE)
            if topic_match:
                self.current_topic = topic_match.group(1).strip()
            else:
                self.current_topic = message.strip()
        if not self.current_topic:
            self.print_styled("I'd be happy to find resources for you. What topic are you interested in?", "assistant")
            return
        self.print_styled(f"Looking for resources on {self.current_topic}...", "assistant")
        self.print_styled("thinking...", "thinking")
        resource_result = self.coordinator.resource_curator.run(
            f"""Find 5 diverse, high-quality learning resources on '{self.current_topic}'.\nOnly include resources that are real and currently accessible on the web.\nDo NOT invent or hallucinate URLs—only include resources you are certain exist, and prefer well-known sites (Wikipedia, YouTube, Coursera, Khan Academy, etc).\nFor each resource, provide:\n- Title\n- Type (article, video, course, etc.)\n- The actual URL (no placeholders)\n- A brief description of what the learner will gain.\nFormat as a plain list."""
        )
        print("\r" + " " * 80)  # Clear the thinking line
        resources = self._get_formatted_resources(resource_result)
        self.print_styled(resources, "assistant")
    
    def set_topic(self, message):
        """Extract and set the current topic from a message"""
        # Try to extract the topic from the message
        topic_match = re.search(r'(learn|study|about|topic|on)\s+([^?.!]+)', message, re.IGNORECASE)
        if topic_match:
            self.current_topic = topic_match.group(2).strip()
        else:
            # If no clear indicator, just use the whole message as topic
            self.current_topic = message.strip()
            
        self.print_styled(f"Great! I'll help you learn about {self.current_topic}. What would you like to know first?", "assistant")
    
    def process_message(self, message):
        """Process user messages and commands"""
        # If we're in the middle of a quiz, treat input as quiz answers
        if self.quiz_in_progress:
            return self.process_quiz_answer(message)
        
        # Special case for markov chain misspelling
        message_lower = message.lower()
        if "mak" in message_lower and "chain" in message_lower and ("quiz" in message_lower or "test" in message_lower or "give" in message_lower or "gime" in message_lower):
            self.current_topic = "Markov Chain"
            self.start_quiz()
            return True
        
        # Detect user intent
        intent = self._detect_intent(message)
        
        # Handle different intents
        if intent == "quit":
            self.print_styled("Thank you for learning with me today. Goodbye!", "assistant")
            return False
            
        elif intent == "help":
            self.show_welcome()
            return True
            
        elif intent == "quiz":
            if self.current_topic:
                self.start_quiz()
            else:
                self.print_styled("I'd be happy to create a quiz. What topic would you like to quiz yourself on?", "assistant")
            return True
            
        elif intent == "resources":
            self.find_resources(message)
            return True
            
        elif intent == "set_topic":
            # Topic was already set in _detect_intent
            self.print_styled(f"I'll help you learn about {self.current_topic}. What specifically would you like to know?", "assistant")
            return True
            
        elif intent == "learn_session":
            self.run_learning_session()
            return True
        
        # For general queries, route to the appropriate agent
        else:
            # If no topic is set yet, try to extract it from the message
            if not self.current_topic:
                topic_match = re.search(r'(?:about|on|what is|how does)\s+([^?.,]+)', message)
                if topic_match:
                    self.current_topic = topic_match.group(1).strip()
            # Determine which agent should handle this query
            query_type = self._detect_query_type(message)
            self.print_styled("thinking...", "thinking")
            # Route to appropriate agent
            if query_type == "resource":
                self.find_resources(message)
                return True
            elif query_type == "assessment":
                # If this is a request for a quiz, handle it directly
                if "quiz" in message.lower() and not message.lower().startswith("what is"):
                    print("\r" + " " * 80)  # Clear the thinking line
                    self.start_quiz()
                    return True
                response = self.coordinator.assessment_agent.run(message)
                formatted_response = response
            elif query_type == "motivation":
                response = self.coordinator.motivation_agent.run(message)
                formatted_response = response
            else:  # concept
                response = self.coordinator.concept_explorer.run(message)
                formatted_response = response
            print("\r" + " " * 80)  # Clear the thinking line
            self.print_styled(formatted_response, "assistant")
            return True
    
    def start(self):
        """Start the chat interface"""
        self.show_welcome()
        
        running = True
        while running:
            try:
                user_input = input("\n> ")
                self.print_styled(user_input, "user")
                running = self.process_message(user_input)
            except KeyboardInterrupt:
                print("\n\nExiting gracefully...")
                break
            except Exception as e:
                self.print_styled(f"An error occurred: {str(e)}. Let's continue our conversation.", "system")

if __name__ == "__main__":
    chat = SmartChat()
    chat.start()