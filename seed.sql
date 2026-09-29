USE campusmate;

INSERT INTO users (email, password_hash, name, is_admin) VALUES
('admin@campusmate.local', 'pbkdf2:sha256:600000$campusmateadmin$GsdzwPycK2EllB4tUn1iFpbHJxzi4kghQa8WCj02nyw', 'CampusMate Admin', TRUE);

INSERT INTO notices (title, content, category, priority) VALUES
('Semester registration window opened', 'Course registration is now available through the department office. Check your academic schedule before submitting your final list.', 'Academic', 'Important'),
('Campus library extended hours', 'The central library will remain open until 9:00 PM during the current assessment period.', 'Campus', 'Normal'),
('Inter-university programming contest', 'Registration is open for students interested in representing the university in the upcoming programming contest.', 'Competition', 'Normal'),
('Maintenance notice: Main building', 'The east-side lift will be under maintenance this week. Please use the central staircase when possible.', 'Maintenance', 'Urgent');

INSERT INTO events (title,date,time,location,description,category,max_seats) VALUES
('Campus Innovation Meetup', '2026-10-03', '15:00:00', 'Innovation Lab', 'A practical meetup for students interested in technology, startups and campus problem solving.', 'Technology', 80),
('Freshers Networking Evening', '2026-10-09', '17:30:00', 'University Auditorium', 'Meet students from different departments and explore campus communities.', 'Community', 150),
('Programming Contest Bootcamp', '2026-10-15', '10:00:00', 'CSE Lab 2', 'Hands-on competitive programming practice covering problem solving and contest strategy.', 'Academic', 60),
('Career & Internship Fair', '2026-10-22', '11:00:00', 'Main Field', 'Connect with employers, explore internships and learn about early-career opportunities.', 'Career', 200);

INSERT INTO clubs (name,description,members_count) VALUES
('CSE Programming Club','Practice algorithms, programming contests and collaborative coding.',86),
('Photography Society','Campus photography walks, editing sessions and creative showcases.',54),
('Robotics & Automation Club','Build practical robotics projects and learn embedded systems.',72),
('Debate & Public Speaking Club','Weekly speaking practice, debates and communication workshops.',63);

INSERT INTO study_groups (subject,group_name,members_count,meeting_time) VALUES
('Operating Systems','OS Exam Sprint',8,'Sunday · 7:00 PM'),
('Database Systems','SQL Study Circle',6,'Monday · 6:30 PM'),
('Web Programming','Full Stack Practice',10,'Tuesday · 8:00 PM'),
('Artificial Intelligence','ML Reading Group',7,'Wednesday · 7:30 PM');

INSERT INTO resources (title,subject,description,resource_url) VALUES
('SQL Quick Reference','Database Systems','Common SELECT, JOIN, GROUP BY and filtering patterns for revision.','https://dev.mysql.com/doc/'),
('Operating Systems Revision Sheet','Operating Systems','Short revision material for process synchronization and scheduling.','https://pages.cs.wisc.edu/~remzi/OSTEP/'),
('Flask Documentation','Web Programming','Official Flask documentation for routing, templates and request handling.','https://flask.palletsprojects.com/');
