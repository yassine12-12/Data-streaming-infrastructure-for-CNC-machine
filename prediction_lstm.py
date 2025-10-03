from lstm_autoencoder import RecurrentAutoencoder
import seaborn as sns
import pandas as pd

model = RecurrentAutoencoder()
path_model = r"FaustAI/model_noise.pth"



df_test = pd.read_json(r'C:\Users\yassine\Desktop\touo\sensordata_3.json')
#print("type ooooo ",type(df_test))

df_noise_test = df_test[["Noise"]].values.astype('float32')


#print("type ooooo ",type(df_noise_test),df_noise_test)  # np array 
#sensor_data = None
THRESHOLD = 0.1

#sensor_data = 5 datapunkte
#for data in sensor_data:
    ## Predictions
    #predictions, pred_losses = self.predict(model, self.test_normal_dataset)
predictions, pred_losses = model.predict(path_model, df_noise_test)
sns.distplot(pred_losses, bins=50, kde=True)
correct = sum(l <= THRESHOLD for l in pred_losses)

#print("predicti",predictions)


#print(f'Correct normal predictions: {correct}/{len(df_noise_test)}')

#print("type ",type(predictions))
#print("Individual prediction values:")
for prediction in predictions:
    c=prediction.item()
    print("predi",c)  # Print the value as a float
print("org",df_noise_test)  # Print the value as a float


