# Savvy (savvy-backend)
Backend for Savvy, a mobile app where Cornell students can view job listings and opportunities centralized

Link to Frontend Repo: https://github.com/vinnie4k/savvy-ios
Link to Figma Design: https://www.figma.com/file/nALQRevFIF7znqAApD9gyd/Hack-Challenge-SP23?node-id=1%3A4&t=Dhkm1qgwtIAFmfF2-1

# Screenshots:

<img src="https://user-images.githubusercontent.com/118781810/236640011-7039336b-4c1e-44cf-bce9-3db147e4fb95.jpeg" width=30%, height=30%> <img src="https://user-images.githubusercontent.com/118781810/236640019-19cb59b2-c23e-42c2-8a75-28da14c4e89e.jpeg" width=30%, height=30%> <img src="https://user-images.githubusercontent.com/118781810/236640023-f44c375f-55e6-4d40-a61a-9313f28d7ade.jpeg" width=30%, height=30%> <img src="https://user-images.githubusercontent.com/118781810/236640025-5b318e8d-4d77-4dd7-80ef-2a09997c0078.jpeg" width=30%, height=30%> <img src="https://user-images.githubusercontent.com/118781810/236640517-84df6b8b-dbce-430b-8698-adc6d9abc6c1.jpeg" width=30%, height=30%> <img src="https://user-images.githubusercontent.com/118781810/236640539-7f23af9c-19b6-483b-b434-73f7aa49ae7a.jpeg" width=30%, height=30%>

# Description:
Savvy is the next big step to creating a more convenient environment for job-seekers, bridging the gap between students and available jobs on campus. Whether it’s your everyday cafe or library job, or research positions with your favorite professor, or even volunteer jobs and short positions posted by other student-led project teams, you can browse them all through the Savvy app.

# Features:
- User Profile w/ Google Log-in
- Job Postings/Descriptions & Filtering Feature
- Bookmarking & Saving to Applied Jobs
- Tags for Types of Job Positions
- Viewing External Site for Job Offering

# Requirements for iOS:
1. SwiftUI
2. Use ScrollView with Stacks (similar to List, discussed with Vin)
3. NavigationLink and NavigationStack to go between screens
4. Used Combine framework, Firebase Authentication, and Native Swift for backend integration

# Requirements for Backend:
1. Many GET and POST routes, includes one DELETE route
2. Includes 4 tables in database (User, Post, Tag, Asset); has many-to-many relationships for User-Post, User-Tag, and Post-Tag
3. API Specification: https://docs.google.com/document/d/1F3Bj1XD2qRo2KP_hmWSBTomrQEM78KcsMDQW2-z_ZMo/edit?usp=sharing
4. Implemented images through the Asset model
