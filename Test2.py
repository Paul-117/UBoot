p1 = real_stock_price_volume[:,0]
v1 = real_stock_price_volume[:,1]
p2 = predicted_stock_price_volume[:,0]
v2 = predicted_stock_price_volume[:,1]

plt.figure(1)
plt.plot(p1, color = 'red', label = 'p1')
plt.title('Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('Stock Price')

plt.figure(2)
plt.plot(v1, color = 'brown', label = 'v1')
plt.title('Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('Stock Price')

plt.figure(3)
plt.plot(p2, color = 'blue', label = 'p2')
plt.title('Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('Stock Price')

plt.figure(4)
plt.plot(v2, color = 'green', label = 'v2')
plt.title('Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('Stock Price')
plt.legend()

plt.show()