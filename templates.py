latex_template = r"""\documentclass[11pt,a4paper,sans]{moderncv}

\moderncvstyle{classic}
\moderncvcolor{blue}

\usepackage[scale=0.75]{geometry}
\setlength{\footskip}{136.00005pt}

\ifxetexorluatex
  \usepackage{fontspec}
  \usepackage{unicode-math}
  \defaultfontfeatures{Ligatures=TeX}
  \setmainfont{Latin Modern Roman}
  \setsansfont{Latin Modern Sans}
  \setmonofont{Latin Modern Mono}
  \setmathfont{Latin Modern Math} 
\else
  \usepackage[T1]{fontenc}
  \usepackage{lmodern}
\fi

\usepackage[english]{babel}

\name{John}{Doe}
\title{Résumé title}
\born{4 July 1776}
\address{street and number}{postcode city}{country}
\phone[mobile]{+1~(234)~567~890}
\phone[fixed]{+2~(345)~678~901}
\phone[fax]{+3~(456)~789~012}
\email{john@doe.org}
\homepage{www.johndoe.com}

\social[linkedin]{john.doe}
\social[xing]{john\_doe}
\social[twitter]{ji\_doe}
\social[github]{jdoe}
\social[gitlab]{jdoe}

\extrainfo{additional information}
\quote{Some quote}

\renewcommand*{\bibliographyitemlabel}{[\arabic{enumiv}]}

\begin{document}

\makecvtitle

\section{Education}
\cventry{year--year}{Degree}{Institution}{City}{\textit{Grade}}{Description}
\cventry{year--year}{Degree}{Institution}{City}{\textit{Grade}}{Description}

\section{Master thesis}
\cvitem{title}{\emph{Title}}
\cvitem{supervisors}{Supervisors}
\cvitem{description}{Short thesis abstract}

\section{Experience}
\cventry{year--year}{Job title}{Employer}{City}{}{General description no longer than 1--2 lines.\newline{}
Detailed achievements:
\begin{itemize}
\item Achievement 1
\item Achievement 2 (with sub-achievements)
  \begin{itemize}
  \item Sub-achievement (a);
  \item Sub-achievement (b), with sub-sub-achievements;
    \begin{itemize}
    \item Sub-sub-achievement i;
    \item Sub-sub-achievement ii;
    \item Sub-sub-achievement iii;
    \end{itemize}
  \item Sub-achievement (c);
  \end{itemize}
\item Achievement 3
\item Achievement 4
\end{itemize}}
\cventry{year--year}{Job title}{Employer}{City}{}{Description line 1\newline{}Description line 2\newline{}Description line 3}
\subsection{Miscellaneous}
\cventry{year--year}{Job title}{Employer}{City}{}{Description}

\section{Languages}
\cvitemwithcomment{Language 1}{Skill level}{Comment}
\cvitemwithcomment{Language 2}{Skill level}{Comment}
\cvitemwithcomment{Language 3}{Skill level}{Comment}
\cvitemwithcomment{Language 4}{Skill level}{Comment}

\section{Computer skills}
\cvdoubleitem{category 1}{XXX, YYY, ZZZ}{category 4}{XXX, YYY, ZZZ}
\cvdoubleitem{category 2}{XXX, YYY, ZZZ}{category 5}{XXX, YYY, ZZZ}
\cvdoubleitem{category 3}{XXX, YYY, ZZZ}{category 6}{XXX, YYY, ZZZ}

\section{Skill matrix}
\cvitem{Skill matrix}{Alternatively, provide a skill matrix to show off your skills}

\cvskilllegend*[1em]{}

\cvskillhead[-0.1em]

\cvskillentry*{Language:}{3}{Python}{2}{I'm so experienced in Python and have realised a million projects. At least.}
\cvskillentry{}{2}{Lilypond}{14}{So much sheet music! Man, I'm the best!}
\cvskillentry{}{3}{\LaTeX}{14}{Clearly I rock at \LaTeX}
\cvskillentry*{OS:}{3}{Linux}{2}{I only use Archlinux btw}
\cvskillentry*[1em]{Methods}{4}{SCRUM}{8}{SCRUM master for 5 years}

\section{Interests}
\cvitem{hobby 1}{Description}
\cvitem{hobby 2}{Description}
\cvitem{hobby 3}{Description}

\section{Extra 1}
\cvlistitem{Item 1}
\cvlistitem{Item 2}
\cvlistitem{Item 3. This item is particularly long and therefore normally spans over several lines. Did you notice the indentation when the line wraps?}

\section{Extra 2}
\cvlistdoubleitem{Item 1}{Item 4}
\cvlistdoubleitem{Item 2}{Item 5\cite{book2}}
\cvlistdoubleitem{Item 3}{Item 6. Like item 3 in the single column list before, this item is particularly long to wrap over several lines.}

\section{References}
\begin{cvcolumns}
  \cvcolumn{Category 1}{\begin{itemize}\item Person 1\item Person 2\item Person 3\end{itemize}}
  \cvcolumn{Category 2}{Amongst others:\begin{itemize}\item Person 1, and\item Person 2\end{itemize}(more upon request)}
  \cvcolumn[0.5]{All the rest \& some more}{\textit{That} person, and \textbf{those} also (all available upon request).}
\end{cvcolumns}

\nocite{*}
\bibliographystyle{plain}
\bibliography{publications}

\end{document}"""

john_doe_resume = """
John Doe

[Email: johndoe@example.com] | [Phone: +44 123 456 7890] | [LinkedIn: linkedin.com/in/johndoe] | [GitHub: github.com/johndoe]
London, UK

PROFESSIONAL SUMMARY

Passionate and detail-oriented Software Engineer with 5+ years of experience designing, developing, and implementing scalable and efficient software solutions. Adept at collaborating with cross-functional teams, writing clean code, and leveraging cutting-edge technologies to drive business success. Skilled in back-end development, API integrations, and cloud computing.

TECHNICAL SKILLS

Programming Languages: Python, JavaScript, Java, C++
Frameworks & Libraries: React.js, Node.js, Django, Spring Boot
Databases: MySQL, PostgreSQL, MongoDB
DevOps & Cloud: Docker, Kubernetes, AWS, Azure, CI/CD pipelines
Tools: Git, JIRA, Jenkins, Elasticsearch, Redis

PROFESSIONAL EXPERIENCE

Software Engineer

Tech Innovators Ltd., London, UK
June 2020 – Present
	•	Designed and implemented scalable APIs that improved system performance by 25%.
	•	Migrated legacy systems to cloud-based architecture, reducing downtime by 30%.
	•	Developed and deployed automated CI/CD pipelines, speeding up software delivery cycles by 40%.
	•	Collaborated with product managers to gather requirements and optimize user experience.

Junior Software Engineer

Digital Solutions Inc., London, UK
August 2018 – May 2020
	•	Built responsive front-end applications using React.js, improving user engagement by 15%.
	•	Debugged and resolved critical back-end issues, ensuring 99.9% uptime for client systems.
	•	Conducted code reviews and implemented best practices to maintain high-quality codebases.
	•	Developed scripts to automate routine tasks, saving over 10 hours of manual work per week.

EDUCATION

Bachelor of Science in Computer Science
University College London (UCL)
Graduated: 2018

PROJECTS

E-commerce Platform:
	•	Built a full-stack e-commerce web app using React.js, Node.js, and MongoDB.
	•	Implemented a recommendation engine using machine learning to boost sales by 20%.

IoT Device Management System:
	•	Designed a cloud-based dashboard to monitor and manage IoT devices, improving reliability by 30%.

CERTIFICATIONS
	•	AWS Certified Solutions Architect – Associate
	•	Certified Kubernetes Administrator (CKA)
	•	React Developer Certification

PERSONAL ATTRIBUTES
	•	Strong problem-solving skills with a passion for continuous learning.
	•	Excellent team player with a proven ability to collaborate across departments.
	•	Effective communicator, capable of presenting technical concepts to non-technical audiences.

Let me know if you’d like any specific adjustments!
"""