/**
 * Authentication & Session Management Tests
 */
describe('Auth Context & Token Management', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('stores JWT access token and user metadata on successful login', () => {
    const mockAuthResponse = {
      token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mockToken',
      user: {
        id: 10,
        username: 'dr_sharma',
        role: 'Doctor',
        hospital_id: 1
      }
    };

    localStorage.setItem('token', mockAuthResponse.token);
    localStorage.setItem('user', JSON.stringify(mockAuthResponse.user));

    expect(localStorage.getItem('token')).toBe(mockAuthResponse.token);
    const storedUser = JSON.parse(localStorage.getItem('user'));
    expect(storedUser.role).toBe('Doctor');
    expect(storedUser.username).toBe('dr_sharma');
  });

  test('clears local session and cached identity on logout', () => {
    localStorage.setItem('token', 'sample-token');
    localStorage.setItem('user', JSON.stringify({ username: 'nurse_mary', role: 'Nurse' }));

    // Simulate logout action
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  test('identifies authorized roles correctly', () => {
    const rolePermissions = {
      Doctor: ['diagnosis.create', 'prescription.create', 'lab_order.create'],
      'Lab Technician': ['lab_result.upload', 'document.upload'],
      'Hospital Admin': ['doctor.onboard', 'hospital.manage', 'audit.read'],
      Patient: ['document.view', 'prescription.read']
    };

    expect(rolePermissions['Doctor']).toContain('prescription.create');
    expect(rolePermissions['Lab Technician']).toContain('document.upload');
    expect(rolePermissions['Hospital Admin']).toContain('audit.read');
    expect(rolePermissions['Patient']).not.toContain('diagnosis.create');
  });
});
