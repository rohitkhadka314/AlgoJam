import numpy as np


class Algorithm():
    def __init__(self, positions):
        self.data = {}  # Historical data of all instruments
        self.positionLimits = {}  # Initialise position limits
        self.day = 0  # Initialise the current day as 0
        self.positions = positions  # Initialise the current positions

    def get_current_price(self, instrument):
        """
        Helper function to fetch current price of an instrument.
        """
        return self.data[instrument][-1]

    def _mean_reversion_signal(self, instrument, lookback, thresh):
        history = self.data[instrument]
        if len(history) < lookback + 1:
            return 0
        # Exclude the current day to avoid lookahead bias, match the backtest logic: p[i-lookback:i] compared to p[i-1]
        # In the backtest, at day i, p[i-1] is the latest known price.
        # history[-1] is the latest known price at `self.day`.
        # history[-lookback-1:-1] is the window.
        window_hist = np.array(history[-lookback-1:-1], dtype=float)
        mean = window_hist.mean()
        std = window_hist.std()
        if std == 0:
            return 0
        z = (history[-1] - mean) / std
        if z > thresh:
            return -1
        elif z < -thresh:
            return 1
        return 0

    def _momentum_signal(self, instrument, lookback):
        history = self.data[instrument]
        if len(history) < lookback + 1:
            return 0
        window_hist = np.array(history[-lookback-1:-1], dtype=float)
        mean = window_hist.mean()
        if history[-1] > mean:
            return 1
        else:
            return -1

    def _scaled_position(self, instrument, signal):
        if signal == 0:
            return 0
        limit = self.positionLimits.get(instrument, 0)
        # Use a conservative fraction of the limit to leave room in the budget
        frac = 0.50 if instrument != "Liferaft Ticket" else 1.0
        raw_units = int(round(limit * frac))
        return raw_units if signal > 0 else -raw_units

    def get_positions(self):
        positionLimits = self.positionLimits
        desiredPositions = {instrument: 0 for instrument in positionLimits}

        if self.day < 20:
            return desiredPositions

        signals = {}
        for instrument in positionLimits:
            if instrument == "Boat Party Ticket":
                signal = self._mean_reversion_signal(instrument, lookback=5, thresh=0.5)
            elif instrument == "Bread":
                signal = self._momentum_signal(instrument, lookback=10)
            elif instrument == "Fintech Token":
                signal = self._mean_reversion_signal(instrument, lookback=5, thresh=0.5)
            elif instrument == "Liferaft Ticket":
                signal = self._momentum_signal(instrument, lookback=3)
            elif instrument == "MenuDash":
                signal = self._mean_reversion_signal(instrument, lookback=10, thresh=0.5)
            elif instrument == "Sausage Sizzle":
                signal = self._momentum_signal(instrument, lookback=20)
            elif instrument == "Sausage":
                signal = self._momentum_signal(instrument, lookback=10)
            elif instrument == "Thrifted Jeans":
                signal = self._momentum_signal(instrument, lookback=10)
            elif instrument == "UQ Dollar":
                signal = self._mean_reversion_signal(instrument, lookback=10, thresh=0.5)
            else:
                signal = 0
            
            signals[instrument] = signal

        for instrument, signal in signals.items():
            desiredPositions[instrument] = self._scaled_position(instrument, signal)

        # Keep overall notional exposure well below the hard budget cap.
        notional = 0
        for instrument in desiredPositions:
            notional += abs(desiredPositions[instrument]) * self.get_current_price(instrument)

        # 600,000 is the hard limit. Scale down if over 500,000 to be safe.
        if notional > 500000:
            scale = 500000 / max(notional, 1e-9)
            for instrument in desiredPositions:
                desiredPositions[instrument] = int(round(desiredPositions[instrument] * scale))
                if desiredPositions[instrument] != 0 and abs(desiredPositions[instrument]) < 1:
                    desiredPositions[instrument] = 0

        return desiredPositions
