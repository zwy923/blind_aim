class PID:
    def __init__(self, dt, max, min, p, i, d):
        self.dt = dt
        self.max = max
        self.min = min
        self.Kp = p  
        self.Ki = i 
        self.Kd = d  
        self.integral = 0  
        self.pre_error = 0  

    def calculate(self, setPoint, pv):
        error = setPoint - pv 
        Pout = self.Kp * error 
        self.integral += error * self.dt
        Iout = self.Ki * self.integral
        derivative = (error - self.pre_error) / self.dt
        Dout = self.Kd * derivative
        output = Pout + Iout + Dout

        if (output > self.max):
            output = self.max
        elif (output < self.min):
            output = self.min

        self.pre_error = error
        return output

