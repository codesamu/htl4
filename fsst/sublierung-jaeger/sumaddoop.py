class Person:
    def __init__(self, name, ort, vorname):
        self.name = name
        self.ort= ort
        self.vorname=vorname

    def ich_bin(self):
        print(f"Mein name ist {self.name}.")

    def mein_ort(self):
        print(f"Ich komme aus {self.ort}.")

class student(Person):
    def __init__(self, name, ort, vorname, eintritt):
        super().__init__(name,ort,vorname)
        self.eintritt=eintritt

    def ich_bin(self):
        print(f"Ich bin {self.name} {self.vorname} und gehe seit {self.eintritt} in die HTL")


n= Person("Voetter","Fulpmes","Nadine")
n.ich_bin()
# n.mein_ort()
s=student("Samuel","Baumkirchen", "Fronthaler", 2022)
s.ich_bin()
