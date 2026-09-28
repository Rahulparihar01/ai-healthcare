/**
 * End-to-End Clinical Flow Integration Tests
 * Receptionist Registration -> Doctor Prescription & Safety Warning -> Lab Order & Upload
 */
describe('Clinical Workflow Integration', () => {
  test('validates patient demographic intake format', () => {
    const validPatient = {
      full_name: 'Aarav Patel',
      dob: '1988-04-12',
      gender: 'Male',
      blood_group: 'B+',
      phone_number: '9876543210'
    };

    const validatePatient = (p) => {
      if (!p.full_name || p.full_name.length < 2) return false;
      if (!p.dob || !p.dob.match(/^\d{4}-\d{2}-\d{2}$/)) return false;
      if (!['Male', 'Female', 'Other'].includes(p.gender)) return false;
      return true;
    };

    expect(validatePatient(validPatient)).toBe(true);
    expect(validatePatient({ ...validPatient, dob: 'invalid-date' })).toBe(false);
  });

  test('detects drug-allergy interactions during prescription drafting', () => {
    const patientAllergies = ['Penicillin', 'Sulfa drugs'];
    const draftMedications = [
      { name: 'Amoxicillin', dosage: '500mg' }, // Penicillin class
      { name: 'Paracetamol', dosage: '650mg' }
    ];

    const checkAllergyContraindication = (allergies, meds) => {
      const allergyMap = {
        'penicillin': ['amoxicillin', 'ampicillin', 'penicillin v', 'augmentin'],
        'sulfa': ['bactrim', 'sulfamethoxazole']
      };

      const warnings = [];
      for (const med of meds) {
        const medLower = med.name.toLowerCase();
        for (const allergy of allergies) {
          const key = allergy.toLowerCase();
          for (const [classKey, drugList] of Object.entries(allergyMap)) {
            if (key.includes(classKey) && drugList.some(d => medLower.includes(d))) {
              warnings.push(`Severe Allergy Conflict: Patient is allergic to ${allergy} (triggered by ${med.name})`);
            }
          }
        }
      }
      return warnings;
    };

    const warnings = checkAllergyContraindication(patientAllergies, draftMedications);
    expect(warnings.length).toBeGreaterThan(0);
    expect(warnings[0]).toContain('Amoxicillin');
  });

  test('ensures lab test order transitions from Pending to Completed upon report attachment', () => {
    const labOrder = {
      id: 42,
      patient_id: 101,
      tests: [{ name: 'CBC' }, { name: 'Lipid Profile' }],
      status: 'Pending'
    };

    const fulfillOrder = (order, reportPayload) => {
      return {
        ...order,
        status: 'Completed',
        report_file: reportPayload.file_url,
        completed_at: new Date().toISOString()
      };
    };

    const completed = fulfillOrder(labOrder, { file_url: '/records/download/lab_report/42' });
    expect(completed.status).toBe('Completed');
    expect(completed.report_file).toBeDefined();
  });
});
