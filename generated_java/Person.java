import java.util.Date;

public abstract class Person extends Professor {
    private String name;
    private Date dob;

    public Person(String employeeId, String department, String name, Date dob) {
        super(employeeId, department);
        this.name = name;
        this.dob = dob;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Date getDob() {
        return dob;
    }

    public void setDob(Date dob) {
        this.dob = dob;
    }

}
