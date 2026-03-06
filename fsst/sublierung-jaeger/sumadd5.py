nums=[]
i= 0

while True:
    uinp= input(f"Bitte die {i+1}. Zahl eingeben: ")
    if uinp== "x":
        break

    try:
        uint= int(uinp)
        nums.append(uint)
        i += 1
    except:
        print(f"bitte eine Zahl oder x eingeben")

print(nums)
print(sum(nums))
print("avg is: ", (sum(nums)/len(nums)))

