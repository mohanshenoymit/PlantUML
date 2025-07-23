import java.util.Date;

public class Student {
    private String studentId;
    private String major;

    public Student(String studentId, String major) {
        this.studentId = studentId;
        this.major = major;
    }

    public String getStudentid() {
        return studentId;
    }

    public void setStudentid(String studentId) {
        this.studentId = studentId;
    }

    public String getMajor() {
        return major;
    }

    public void setMajor(String major) {
        this.major = major;
    }

    public void Student(String name, Date dob, String studentId) {
        // TODO: Implement method logic
    }

    public void enrollCourse(Course course) {
        // TODO: Implement method logic
    }

    public String getStudentId() {
        // TODO: Implement method logic
        return defaultStringValue(); // Placeholder return
    }

    private String defaultStringValue() {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'defaultStringValue'");
    }

}
