from django.test import TestCase

from .models import Student, Advisor


class StudentModelTests(TestCase):
    def setUp(self):
        Student.objects.create(stud_name="allison", comp_id="acf6nb", major="computer science")
        Advisor.objects.create(adv_name="sherriff")

    def test_student_exists(self):
        allison = Student.objects.get(stud_name="allison", comp_id="acf6nb", major="computer science")
        self.assertEqual(allison.testingStudentName(), 'allison')
        self.assertEqual(allison.testingStudentId(), 'acf6nb')
        self.assertEqual(allison.testingStudentMajor(), 'computer science')
    
    #def test_advisor_exists(self):
    #    sherriff = Advisor.objects.get(adv_name="sherriff")
    #    self.assertEqual(sherriff.__str__(), "sherriff")
