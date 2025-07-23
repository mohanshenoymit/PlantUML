public class Professor implements Payable {
    private String employeeId;
    private String department;

    public Professor(String employeeId, String department) {
        this.employeeId = employeeId;
        this.department = department;
    }

    public String getEmployeeid() {
        return employeeId;
    }

    public void setEmployeeid(String employeeId) {
        this.employeeId = employeeId;
    }

    public String getDepartment() {
        return department;
    }

    public void setDepartment(String department) {
        this.department = department;
    }

    public void teachCourse(Course course) {
        // TODO: Implement method logic
    }

    public void assignGrade(Student student, Course course, String grade) {
        // TODO: Implement method logic
    }

    @Override
    public double calculateSalary() {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'calculateSalary'");
    }

    @Override
    public void payTax(double amount) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'payTax'");
    }

}
