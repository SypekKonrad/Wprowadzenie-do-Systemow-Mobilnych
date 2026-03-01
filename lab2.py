import matplotlib.pyplot as plt
import numpy as np

arrival_times = [
    0,6,40,30,50,30,25,5,15,15,10,30,40,40,40,50,
    50,55,45,55,55,50,45,45,50,10,25,25,55,55,40,50
]

service_times = [
    40,60,65,60,40,55,65,60,60,70,65,70,65,75,60,50,
    65,65,65,75,70,60,65,62,60,40,55,75,60,40,70,60
]

def simulate_queue(r):

    n = len(arrival_times)
    time = 0

    servers = [0] * r
    queue = []

    lambda_t = []
    mu_t = []
    rho_t = []
    Q_t = []
    W_t = []

    total_wait_time = 0
    served_count = 0
    total_service_time = 0

    while True:

        for i in range(n):
            if arrival_times[i] == time:
                queue.append((i, time))

        for i in range(r):
            if servers[i] == time:
                servers[i] = 0

        for i in range(r):
            if servers[i] == 0 and queue:
                client_id, arrival = queue.pop(0)

                wait = time - arrival
                total_wait_time += wait
                served_count += 1
                total_service_time += service_times[client_id]

                servers[i] = time + service_times[client_id]


        arrived_so_far = sum(1 for a in arrival_times if a <= time)
        lambda_current = arrived_so_far / (time + 1) if time > 0 else 0

        mu_current = (served_count / total_service_time) if total_service_time > 0 else 0

        rho_current = lambda_current / (r * mu_current) if mu_current > 0 else 0

        W_current = total_wait_time / served_count if served_count > 0 else 0

        lambda_t.append(lambda_current)
        mu_t.append(mu_current)
        rho_t.append(rho_current)
        Q_t.append(len(queue))
        W_t.append(W_current)

        time += 1

        # zakończenie gdy wszyscy obsłużeni
        if served_count == n and not queue and all(s == 0 for s in servers):
            break

    return lambda_t, mu_t, rho_t, Q_t, W_t

r = 2 # tu zmieniac wartosc r dla podpunktu c

lambda_t, mu_t, rho_t, Q_t, W_t = simulate_queue(r)


plt.figure()
plt.plot(lambda_t)
plt.plot(mu_t)
plt.title("Zmiany λ oraz μ w czasie")
plt.xlabel("Czas (min)")
plt.ylabel("Wartość")
plt.show()


plt.figure()
plt.plot(rho_t)
plt.title("Zmiany intensywności ruchu ρ w czasie")
plt.xlabel("Czas (min)")
plt.ylabel("ρ")
plt.show()


plt.figure()
plt.plot(Q_t)
plt.plot(W_t)
plt.title("Zmiany Q oraz W w czasie")
plt.xlabel("Czas (min)")
plt.ylabel("Wartość")
plt.show()


print("λ =", lambda_t[-1])
print("μ =", mu_t[-1])
print("ρ =", rho_t[-1])
print("Średnia długość kolejki Q =", np.mean(Q_t))
print("Średni czas oczekiwania W =", np.mean(W_t))
