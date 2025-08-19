import re
import json

def extract_resources(response_text):
    """
    Extract resource information from agent responses.
    Tries multiple approaches to find resources in the text.
    """
    resources = []
    
    # Try to find JSON-formatted resources
    json_pattern = r'\[.*?\]|\{.*?\}'
    json_matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    for match in json_matches:
        try:
            data = json.loads(match)
            if isinstance(data, list) and len(data) > 0:
                for item in data:
                    if isinstance(item, dict) and 'title' in item:
                        resources.append(item)
                if resources:
                    # Filter out fake/placeholder URLs
                    filtered_resources = []
                    for res in resources:
                        url = res.get('url', '')
                        if any(fake in url for fake in ['example.com', 'placeholder', 'fakeurl', 'yourdomain.com']):
                            continue
                        filtered_resources.append(res)
                    if filtered_resources:
                        return filtered_resources
            elif isinstance(data, dict) and 'title' in data:
                resources.append(data)
                return resources
        except:
            pass
    
    # If JSON parsing failed, try regex patterns for common resource formats
    # Pattern 1: Number or bullet followed by title, possibly with URL
    resource_pattern = r'(?:^|\n)(?:\d+\.|\*|\-)\s+(.+?)(?:\s+\((.+?)\))?(?:\s+(?:https?://\S+))?'
    matches = re.findall(resource_pattern, response_text, re.MULTILINE)
    
    if matches:
        for i, (title, res_type) in enumerate(matches):
            url_match = re.search(rf'{re.escape(title)}.*?(https?://\S+)', response_text)
            url = url_match.group(1) if url_match else f"https://example.com/resource{i+1}"
            
            resources.append({
                'title': title.strip(),
                'type': res_type.strip() if res_type else 'resource',
                'url': url
            })
    
    # If still empty, try to extract any URLs with surrounding text
    if not resources:
        url_pattern = r'(https?://\S+)'
        url_matches = re.findall(url_pattern, response_text)
        
        for i, url in enumerate(url_matches):
            # Try to get surrounding text as title
            title_match = re.search(r'([^.!?]+)' + re.escape(url), response_text)
            title = title_match.group(1).strip() if title_match else f"Resource {i+1}"
            
            resources.append({
                'title': title,
                'type': 'resource',
                'url': url
            })
    
    # If still no resources found, create generic ones based on content
    if not resources:
        topic_match = re.search(r'(?:about|on|for)\s+([^.!?,]+)', response_text)
        topic = topic_match.group(1).strip() if topic_match else "this topic"
        
        # Create some placeholder resources
        resources = [
            {
                'title': f"Introduction to {topic.title()}",
                'type': 'article',
                'url': "https://example.com/intro",
                'description': "A beginner-friendly introduction to the topic."
            },
            {
                'title': f"{topic.title()} Tutorial",
                'type': 'video',
                'url': "https://example.com/tutorial",
                'description': "Step-by-step video tutorial for visual learners."
            },
            {
                'title': f"Interactive {topic.title()} Course",
                'type': 'course',
                'url': "https://example.com/course",
                'description': "Hands-on practice with interactive exercises."
            }
        ]
    
    # Filter out fake/placeholder URLs
    filtered_resources = []
    for res in resources:
        url = res.get('url', '')
        if any(fake in url for fake in ['example.com', 'placeholder', 'fakeurl', 'yourdomain.com']):
            continue
        filtered_resources.append(res)
    if filtered_resources:
        return filtered_resources
    # If no real resources, return an empty list
    return []

def extract_subtopics(response_text):
    """
    Extract subtopics from concept explorer responses.
    """
    subtopics = []
    
    # Try to find JSON-formatted subtopics
    json_pattern = r'\[.*?\]|\{.*?\}'
    json_matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    for match in json_matches:
        try:
            data = json.loads(match)
            if isinstance(data, list) and len(data) > 0:
                for item in data:
                    if isinstance(item, dict) and ('name' in item or 'title' in item):
                        name = item.get('name', item.get('title', ''))
                        explanation = item.get('explanation', item.get('description', ''))
                        subtopics.append({'name': name, 'explanation': explanation})
                if subtopics:
                    return subtopics
            elif isinstance(data, dict) and 'subtopics' in data and isinstance(data['subtopics'], list):
                return data['subtopics']
        except:
            pass
    
    # If JSON parsing failed, try regex for numbered or bulleted lists
    # Look for patterns like "1. Subtopic Name: Description" or "• Subtopic Name - Description"
    subtopic_pattern = r'(?:^|\n)(?:\d+\.|\*|\-)\s+([^:.\n]+)(?:[:.-]\s+(.+?))?(?=\n|$)'
    matches = re.findall(subtopic_pattern, response_text, re.MULTILINE)
    
    if matches:
        for name, explanation in matches:
            subtopics.append({'name': name.strip(), 'explanation': explanation.strip()})
    
    # If still no subtopics found, try to extract key phrases
    if not subtopics:
        # Look for capitalized phrases that might be subtopics
        phrase_pattern = r'(?:["\']([A-Z][^"\']{3,})["\']|\*\*([A-Z][^*]{3,})\*\*|(?<=\n)([A-Z][^.\n]{3,}))'
        phrases = re.findall(phrase_pattern, response_text)
        
        for phrase_tuple in phrases:
            phrase = next((p for p in phrase_tuple if p), "")
            if phrase:
                subtopics.append(phrase.strip())
    
    # If still empty, extract any sentences that might be subtopics
    if not subtopics:
        # Extract sentences that might describe subtopics
        sentence_pattern = r'(?<=\n|^)([^.\n]{10,}\.)'
        sentences = re.findall(sentence_pattern, response_text)
        
        for i, sentence in enumerate(sentences[:5]):  # Limit to first 5
            subtopics.append(f"Subtopic {i+1}: {sentence.strip()}")
    
    return subtopics if subtopics else ["Key Aspect 1", "Key Aspect 2", "Key Aspect 3"]

# Add this function to improve quiz parsing


def extract_quiz_questions(response_text):
    """
    Extract quiz questions from assessment agent responses more reliably.
    """
    questions = []
    
    # Try simple extraction first - look for numbered questions
    numbered_questions = re.split(r'\d+\.|Question \d+:', response_text)
    numbered_questions = [q for q in numbered_questions if len(q.strip()) > 10]
    
    if numbered_questions:
        for i, block in enumerate(numbered_questions[:3]):  # Limit to first 3
            question_text = re.search(r'([^ABCD\n]+)\?', block)
            if question_text:
                question = question_text.group(1).strip() + "?"
                
                # Extract options
                options = []
                option_matches = re.findall(r'([A-D])\.?\s+([^\n]+)', block)
                if option_matches:
                    for _, option_text in option_matches:
                        options.append(option_text.strip())
                
                # Find answer
                answer_match = re.search(r'([Cc]orrect|[Aa]nswer)[^A-D]*([A-D])', block)
                answer = "A"  # Default
                if answer_match:
                    answer = answer_match.group(2).upper()
                
                if options:
                    questions.append({
                        "question": question,
                        "options": options[:4],  # Maximum 4 options
                        "answer": answer
                    })
    
    # If the above fails, try JSON extraction
    if not questions:
        json_pattern = r'\[.*?\]|\{.*?\}'
        json_matches = re.findall(json_pattern, response_text, re.DOTALL)
        
        for match in json_matches:
            try:
                data = json.loads(match)
                if isinstance(data, list) and len(data) > 0:
                    for item in data:
                        if isinstance(item, dict) and 'question' in item:
                            questions.append(item)
                    if questions:
                        return questions
                elif isinstance(data, dict):
                    if 'questions' in data and isinstance(data['questions'], list):
                        return data['questions']
                    elif 'question' in data:
                        questions.append(data)
                        return questions
            except:
                pass
    
    # If still empty, use generic questions about the topic
    if not questions:
        # Find topic mentions
        topic_match = re.search(r'(?:about|on|for)\s+[\'\"]?([^\'\".,]+)', response_text)
        topic = topic_match.group(1).strip() if topic_match else "this topic"
        
        # Create topic-specific questions
        questions = [
            {
                "question": f"What is the fundamental concept behind {topic}?",
                "options": [
                    "It's a mathematical model for random processes",
                    "It's a deterministic sequence of states",
                    "It's a machine learning algorithm",
                    "It's a type of data structure"
                ],
                "answer": "A"
            },
            {
                "question": f"Which property is essential for {topic}?",
                "options": [
                    "Complete historical dependence",
                    "Memorylessness (Markov property)",
                    "Deterministic transitions",
                    "Continuous state space"
                ],
                "answer": "B"
            },
            {
                "question": f"How are {topic}s commonly represented?",
                "options": [
                    "Tree diagrams",
                    "Linked lists",
                    "Transition matrices",
                    "Neural networks"
                ],
                "answer": "C"
            }
        ]
    
    return questions

def clean_quiz_response(quiz_text):
    """
    Clean up the quiz text from raw LLM response to make it more parseable
    """
    # Remove metadata markers that might have leaked from the LLM
    cleaned = re.sub(r'content=\'|\'$|additional_kwargs=\{\}|response_metadata=\{[^}]+\}', '', quiz_text)
    
    # Remove any markdown formatting
    cleaned = re.sub(r'\*\*', '', cleaned)
    
    # Fix common formatting issues
    cleaned = cleaned.replace('\\n', '\n')  # Replace escaped newlines
    cleaned = re.sub(r'\s*\n\s*', '\n', cleaned)  # Normalize spacing around newlines
    
    # Ensure option labels are consistent
    cleaned = re.sub(r'\n([A-D])\)', '\n$1. ', cleaned)  # Change "A)" to "A. "
    
    return cleaned

def serpapi_web_search(topic, api_key=None, num_results=5):
    """
    Use SerpApi to perform a Google search and extract real learning resources for a topic.
    Returns a list of dicts with title, url, and snippet.
    """
    try:
        from serpapi import GoogleSearch
    except ImportError:
        return []
    import os
    api_key = api_key or os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return []
    params = {
        "q": f"{topic} learning resource OR tutorial OR course OR article OR video site:edu|site:org|site:com",
        "num": num_results,
        "engine": "google",
        "api_key": api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    resources = []
    for item in results.get("organic_results", [])[:num_results]:
        resources.append({
            "title": item.get("title", "Resource"),
            "url": item.get("link", ""),
            "description": item.get("snippet", "")
        })
    return resources