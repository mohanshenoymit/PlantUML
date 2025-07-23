public class Course {
    private String courseId;
    private String title;
    private int credits;

    public Course(String courseId, String title, int credits) {
        this.courseId = courseId;
        this.title = title;
        this.credits = credits;
    }

    public String getCourseid() {
        return courseId;
    }

    public void setCourseid(String courseId) {
        this.courseId = courseId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public int getCredits() {
        return credits;
    }

    public void setCredits(int credits) {
        this.credits = credits;
    }

    public String getCourseTitle() {
        // TODO: Implement method logic
        return defaultStringValue(); // Placeholder return
    }

}
