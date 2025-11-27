

def perceptron():
    features=[(0,0), (0,1), (1,0), (1,1)]
    labels= [1, 1, 1, 0]

    #Gewichte (Bias, w1, w2)
    w=[0.5,0.5,0.5]

    for epoch in range(10):
        for x,label in zip(features,labels):
            # + Bias
            x=[1]+ list(x)

            #prediction
            y= sum(wi*xi for wi,xi in zip(w,x))
            prediction = 1 if y>0 else 0

            # Weights anpassen
            error= label - prediction
            if error!=0:
                for i in range(len(w)):
                    w[i]+= error*x[i]*0.5 #alpha = 1

        print(f"new weights in epoch {epoch}: {w}")
    return w




weights=perceptron()

def predict(x1,x2,w):
    x=[1,x1,x2]
    y= sum(wi*xi for wi,xi in zip(w,x))
    return 1 if y>0 else 0

print(f"Final weights: {weights}")
print(f"Prediction for (0,0): {predict(0,0,weights)}")
