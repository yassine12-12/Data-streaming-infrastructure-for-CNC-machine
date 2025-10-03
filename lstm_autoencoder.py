#!/usr/bin/env python3

import pandas as pd
from scipy.io import arff
from sklearn.model_selection import train_test_split
import torch
#import lstm_autoencoder as net

import copy
import numpy as np
import pandas as pd
import seaborn as sns
from pylab import rcParams
import matplotlib.pyplot as plt
from matplotlib import rc
from torch import nn, optim

#import funct_lstm_autoencoder as f
from torch.utils.tensorboard import SummaryWriter


writer = SummaryWriter()
 

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Encoder(nn.Module):
  def __init__(self, seq_len, n_features, embedding_dim=64):
    super(Encoder, self).__init__()

    self.seq_len, self.n_features = seq_len, n_features
    self.embedding_dim, self.hidden_dim = embedding_dim, 2 * embedding_dim

    self.rnn1 = nn.LSTM(
      input_size=n_features,
      hidden_size=self.hidden_dim,
      num_layers=1,
      batch_first=True
    )
    
    self.rnn2 = nn.LSTM(
      input_size=self.hidden_dim,
      hidden_size=embedding_dim,
      num_layers=1,
      batch_first=True
    )

  def forward(self, x):
    x = x.reshape((1, self.seq_len, self.n_features))

    x, (_, _) = self.rnn1(x)
    x, (hidden_n, _) = self.rnn2(x)

    return hidden_n.reshape((self.n_features, self.embedding_dim))


class Decoder(nn.Module):

  def __init__(self, seq_len, input_dim=64, n_features=1):
    super(Decoder, self).__init__()

    self.seq_len, self.input_dim = seq_len, input_dim
    self.hidden_dim, self.n_features = 2 * input_dim, n_features

    self.rnn1 = nn.LSTM(
      input_size=input_dim,
      hidden_size=input_dim,
      num_layers=1,
      batch_first=True
    )

    self.rnn2 = nn.LSTM(
      input_size=input_dim,
      hidden_size=self.hidden_dim,
      num_layers=1,
      batch_first=True
    )

    self.output_layer = nn.Linear(self.hidden_dim, n_features)

  def forward(self, x):
    x = x.repeat(self.seq_len, self.n_features)
    x = x.reshape((self.n_features, self.seq_len, self.input_dim))

    x, (hidden_n, cell_n) = self.rnn1(x)
    x, (hidden_n, cell_n) = self.rnn2(x)
    x = x.reshape((self.seq_len, self.hidden_dim))

    return self.output_layer(x)



class RecurrentAutoencoder(nn.Module):

  def __init__(self, embedding_dim=64):
    super(RecurrentAutoencoder, self).__init__()
    ## !!!!!Select the data from the databank!!!!!
    path_to_train_db = r'C:\Users\yassine\Neuer Ordner (2)\daten-streaming-infrastruktur\sensordata_1.json'
    df_train = pd.read_json(path_to_train_db)
    self.df_noise_train = df_train[["Noise"]].values.astype('float32')

    path_to_test_db = r'C:\Users\yassine\Neuer Ordner (2)\daten-streaming-infrastruktur\sensordata_3.json'
    df_test = pd.read_json(path_to_test_db)
    self.df_noise_test = df_test[["Noise"]].values.astype('float32')
    self.train_dataset = None
    self.val_dataset = None
    self.test_normal_dataset = None
    self.test_anomaly_dataset = None

    ##Dataset preparetion
    self.dataset_prepare()
    print(self.seq_len)


    self.encoder = Encoder(self.seq_len, self.n_features, embedding_dim).to(device)
    self.decoder = Decoder(self.seq_len, embedding_dim, self.n_features).to(device)


    self.training = True
    self.pausing = False
    self.training_completed = False

  def forward(self, x):
    x = self.encoder(x)
    x = self.decoder(x)
    return x
  

  
  def data_split(self,RANDOM_SEED =42):
    np.random.seed(RANDOM_SEED)
    torch.manual_seed(RANDOM_SEED)


    train_df, val_df = train_test_split(
      self.df_noise_train,
      test_size=0.15,
      random_state=RANDOM_SEED
    )

    val_df, test_df = train_test_split(
      val_df,
      test_size=0.33, 
      random_state=RANDOM_SEED
    )
    return train_df, val_df, test_df 

  def create_dataset(self,df):
      sequences = df.astype(np.float32).tolist()
      dataset = [torch.tensor(s).unsqueeze(1).float() for s in sequences]
      n_seq, self.seq_len, self.n_features = torch.stack(dataset).shape
      return dataset, self.seq_len, self.n_features


  def dataset_prepare(self):
    train_df, val_df, test_df = self.data_split()

    self.train_dataset, self.seq_len, self.n_features = self.create_dataset(train_df)
    self.val_dataset, _, _ = self.create_dataset(val_df)
    self.test_normal_dataset, _, _ = self.create_dataset(test_df)
    self.test_anomaly_dataset, _, _ = self.create_dataset(self.df_noise_test)
      
  def train_model(self,model_saved_path,n_epochs):

    #model_saved_path="/home/oguz/plotly_gui/plotly/training/lstm_autoencoder/models/model_noise.pth"

    train_dataset = self.train_dataset
    val_dataset = self.val_dataset
    model = self.model

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.L1Loss(reduction='sum').to(device)
    history = dict(train=[], val=[])

    best_model_wts = copy.deepcopy(model.state_dict())
    best_loss = 10000.0
    
    for epoch in range(1, n_epochs + 1):
        ##Start,Pause, Save Training
        if self.training == True and self.pausing == False:

          model = model.train()
          train_losses = []
          for seq_true in train_dataset:
              optimizer.zero_grad()

              seq_true = seq_true.to(device)
              seq_pred = model(seq_true)

              loss = criterion(seq_pred, seq_true)

              loss.backward()
              optimizer.step()

              train_losses.append(loss.item())

          val_losses = []
          model = model.eval()
          with torch.no_grad():
              for seq_true in val_dataset:

                  seq_true = seq_true.to(device)
                  seq_pred = model(seq_true)

                  loss = criterion(seq_pred, seq_true)
                  val_losses.append(loss.item())

          train_loss = np.mean(train_losses)
          val_loss = np.mean(val_losses)

          history['train'].append(train_loss)
          history['val'].append(val_loss)

          if val_loss < best_loss:
              best_loss = val_loss
              best_model_wts = copy.deepcopy(model.state_dict())

          print(f'Epoch {epoch}: train loss {train_loss} val loss {val_loss}')

        elif self.training ==False and self.pausing == True:
          model.save_model(model,model_saved_path)
          break
        elif self.training == False and self.pausing == False:
          break
    self.training_completed = True   
    model.load_state_dict(best_model_wts)

    # Log loss and other metrics
    #writer.add_scalar('Loss', train_loss, epoch)
    #writer.add_scalar('Accuracy', accuracy, epoch)

    # Log histograms of model parameters
    #for name, param in model.named_parameters():
    #    writer.add_histogram(name, param, epoch)

    # Log images, if applicable
  # writer.add_image('Images', image, global_step)


    return model.eval(), history
  




  

  def save_model(self,model,model_path):
    torch.save(model, model_path)
    print("Model is saved under {}".format(model_path))

  def load_model(self,model_path=r".\model_noispy -m e.pth"):
    model = torch.load(model_path)
    return model

  def run_training(self,model_saved_path=r".\model_noise.pth"):
    
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #model = net.RecurrentAutoencoder(self.seq_len, self.n_features, 128)
    self.model = RecurrentAutoencoder(128) 
    self.model = self.model.to(device)
    self.model, history = self.train_model(
      #self.model, 
      #self.train_dataset, 
      #self.val_dataset, 
      model_saved_path,
      n_epochs=5
    )
    if self.training == True and self.pausing == False:
       self.model.save_model(self.model,model_saved_path)
    return    
       
  def predict(self,model_saved_path, sensor_dat):
      ##preperae dataset
      print(len(sensor_dat))
      prediction_df, _, _ = self.create_dataset(sensor_dat)
      model = self.load_model(model_saved_path)

      predictions, losses = [], []
      criterion = nn.L1Loss(reduction='sum').to(device)
      with torch.no_grad():
          model = model.eval()
          #for seq_true in dataset:
          for seq_true in prediction_df:    
              seq_true = seq_true.to(device)
              seq_pred = model(seq_true)

              loss = criterion(seq_pred, seq_true)

              predictions.append(seq_pred.cpu().numpy().flatten())
              losses.append(loss.item())
      return predictions, losses


  # def run_predictions(self, THRESHOLD = 0.1,model_saved_path = "../models/lstm_autoencoder/models/model_noise.pth"):

  #   model = self.load_model(model_saved_path)
  #   ## Predictions
  #   #predictions, pred_losses = self.predict(model, self.test_normal_dataset)
  #   #predictions, pred_losses = self.predict(model, sensor_data)
  #   sns.distplot(pred_losses, bins=50, kde=True);
  #   correct = sum(l <= THRESHOLD for l in pred_losses)
  #   print(f'Correct normal predictions: {correct}/{len(self.test_normal_dataset)}')
