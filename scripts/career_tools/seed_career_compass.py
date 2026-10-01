from career_tools.models import CareerCompassQuestion

# MCTI Career Compass - After 10th
# Pure English question bank.
# Direction mappings must remain unchanged.

QUESTIONS = [
    ('interest', 'If you have free time after school, which activity would interest you the most?', 'Exploring computers, apps or new technology', 'Thinking about buying, selling or a business idea', 'Drawing, designing, making videos or creating content', 'Working with a machine, device or another practical task', 'technology', 'business', 'creative', 'practical'),
    ('interest', 'If you could choose a school project, what type of project would you prefer?', 'A website, coding or digital project', 'A science experiment or research project', 'A presentation, poster or creative campaign', 'Organizing a team for a social activity', 'technology', 'science', 'creative', 'people'),
    ('interest', 'Which activity naturally attracts you the most?', 'Working with numbers, money and planning', 'Understanding science facts and how things work', 'Talking with people and helping them', 'Working with tools, equipment or hands-on tasks', 'business', 'science', 'people', 'practical'),
    ('interest', 'If a school event is being organized, which role would you choose?', 'Managing registration, data or technology', 'Managing the budget and expenses', 'Creating posters, stage designs or social-media content', 'Coordinating with students and guests', 'technology', 'business', 'creative', 'people'),
    ('interest', 'If you were watching educational content on YouTube, which topic would you most likely choose?', 'AI, computers and technology', 'Business, money and entrepreneurship', 'Science discoveries and experiments', 'Design, animation, photography or media', 'technology', 'business', 'science', 'creative'),
    ('interest', 'Which result would give you the most satisfaction?', 'Guiding or helping someone', 'Repairing, building or installing something yourself', 'Solving a difficult problem logically', 'Creating something original and attractive', 'people', 'practical', 'science', 'creative'),
    ('subject', 'In school subjects, which type of work feels most comfortable to you?', 'Mathematics and logical exercises', 'Science concepts and experiments', 'Languages, presentations and communication', 'Drawing, craft and visual work', 'technology', 'science', 'people', 'creative'),
    ('subject', 'When working with numbers, what interests you the most?', 'Finding patterns and logical solutions', 'Calculating profit, prices, budgets and money', 'Taking measurements for practical work', 'Presenting data through graphs or designs', 'technology', 'business', 'practical', 'creative'),
    ('subject', 'When studying a science chapter, what interests you the most?', 'Understanding the reasons and logic', 'Performing an experiment and observing the result', 'Understanding how it is used in technology', 'Explaining the concept to others', 'science', 'practical', 'technology', 'people'),
    ('subject', 'When learning a difficult topic, which method works best for you?', 'Exploring it through a computer, video or tutorial', 'Analyzing the concept in detail', 'Discussing it with a teacher or friend', 'Learning by doing and practising yourself', 'technology', 'science', 'people', 'practical'),
    ('subject', 'In a school assignment, where are your strengths most likely to be?', 'Calculations and structured problem solving', 'Planning, costing and organizing', 'Writing, speaking and explaining', 'Presentation and visual creativity', 'science', 'business', 'people', 'creative'),
    ('subject', 'If you could learn a new skill, which type would appeal to you the most?', 'Coding, software or digital tools', 'Accounting or business management', 'Graphic design, video or content creation', 'Technical equipment or a practical trade skill', 'technology', 'business', 'creative', 'practical'),
    ('problem_solving', 'When you face a problem, what is your natural first approach?', 'Find a step-by-step logical solution', 'Understand the reason scientifically', 'Discuss it with an experienced person', 'Try it yourself and find a practical solution', 'technology', 'science', 'people', 'practical'),
    ('problem_solving', 'A school event is running short of budget. What would you prefer to do?', 'Analyze the expenses and numbers', 'Think of sponsorship or fundraising ideas', 'Discuss it with the team and find a solution', 'Create a low-cost creative alternative', 'science', 'business', 'people', 'creative'),
    ('problem_solving', 'If your computer or mobile phone develops a problem, what would you generally prefer to do?', 'Check settings or online solutions and troubleshoot it', 'Understand the exact technical reason for the problem', 'Explain the issue to a knowledgeable person and seek help', 'Check the device yourself and try a practical solution', 'technology', 'science', 'people', 'practical'),
    ('problem_solving', 'Everyone in a group project has different ideas. Which role would suit you best?', 'Compare the options and make a logical choice', 'Decide according to time, budget and resources', 'Listen to everyone and try to build agreement', 'Combine different ideas into a unique solution', 'science', 'business', 'people', 'creative'),
    ('problem_solving', 'You are given an unfamiliar task. What would you prefer to do?', 'Explore a solution using digital tools', 'Plan the resources and then begin', 'Try different possibilities creatively', 'Watch a demonstration and then try it hands-on', 'technology', 'business', 'creative', 'practical'),
    ('problem_solving', 'Your friend is struggling with a topic. How would you prefer to help?', 'Find a useful app, video or learning resource', 'Explain the logic behind the concept', 'Listen patiently and guide your friend', 'Show a practical example', 'technology', 'science', 'people', 'practical'),
    ('work_style', 'What type of environment might suit you best in your future work?', 'Working with computers and digital systems', 'Working with targets, business and decision-making', 'Working with ideas, visuals and creative freedom', 'Working with people and teamwork', 'technology', 'business', 'creative', 'people'),
    ('work_style', 'How might you prefer to work?', 'Systematically with data and logic', 'With research and analysis', 'Hands-on with tools and equipment', 'Through communication and interaction', 'technology', 'science', 'practical', 'people'),
    ('work_style', 'In a group activity, which responsibility would you naturally choose?', 'Technical or digital work', 'Planning, budgeting or leadership', 'Design and presentation', 'Coordination and communication', 'technology', 'business', 'creative', 'people'),
    ('work_style', 'Which task would feel comparatively less boring to you?', 'Analyzing information', 'Creating a business plan', 'Developing a creative concept', 'Assembling, installing or operating something', 'science', 'business', 'creative', 'practical'),
    ('work_style', 'In which situation would you feel the greatest sense of achievement?', 'My digital solution works properly', 'My planning produces a good result or profit', 'My creation impresses people', 'My guidance helps someone', 'technology', 'business', 'creative', 'people'),
    ('work_style', 'If you had an internship opportunity, which environment would you explore first?', 'IT or software', 'Business, accounting or office work', 'Laboratory or research', 'Workshop or technical work', 'technology', 'business', 'science', 'practical'),
    ('environment', 'What type of problems can you imagine yourself solving in the future?', 'Technology and digital problems', 'Business and financial problems', 'Scientific and analytical problems', 'People and communication problems', 'technology', 'business', 'science', 'people'),
    ('environment', 'If you could choose your future workplace, which environment sounds most interesting?', 'A technology company', 'A business or corporate office', 'A creative studio or media environment', 'A technical workshop or work site', 'technology', 'business', 'creative', 'practical'),
    ('environment', 'What might feel most meaningful to you in your future career?', 'Growing with new technology', 'Building or managing a business', 'Finding solutions through knowledge and research', 'Teaching, guiding or supporting people', 'technology', 'business', 'science', 'people'),
    ('environment', 'If you could shadow a professional for one day, whom would you choose?', 'A software or IT professional', 'An entrepreneur or accounting professional', 'A designer or media professional', 'An engineer or technician doing hands-on work', 'technology', 'business', 'creative', 'practical'),
    ('environment', 'What type of output might you enjoy creating in your future career?', 'An app, website, digital system or data solution', 'A business result, sales plan or financial plan', 'A research finding or analytical solution', 'A design, video, artwork or creative content', 'technology', 'business', 'science', 'creative'),
    ('environment', 'Which future activity sounds most interesting to you?', 'Communicating with and guiding a team or customers', 'Operating machines, equipment or technical systems', 'Identifying a business opportunity', 'Investigating a scientific question', 'people', 'practical', 'business', 'science'),
]

for order, row in enumerate(QUESTIONS, start=1):
    (
        dimension, question,
        a, b, c, d,
        da, db, dc, dd
    ) = row

    CareerCompassQuestion.objects.update_or_create(
        order=order,
        defaults={
            "dimension": dimension,
            "question": question,
            "option_a": a,
            "option_b": b,
            "option_c": c,
            "option_d": d,
            "direction_a": da,
            "direction_b": db,
            "direction_c": dc,
            "direction_d": dd,
            "is_active": True,
        }
    )

print(
    "Career Compass questions:",
    CareerCompassQuestion.objects.filter(is_active=True).count()
)
