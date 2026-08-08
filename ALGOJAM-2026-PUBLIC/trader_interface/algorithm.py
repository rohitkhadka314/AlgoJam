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

    def _rolling_zscore(self, instrument, window=20):
        history = self.data[instrument]
        if len(history) < window + 1:
            return 0.0
        window_hist = np.array(history[-window:], dtype=float)
        mean = window_hist.mean()
        std = window_hist.std()
        if std == 0:
            return 0.0
        return (history[-1] - mean) / std

    def _trend_signal(self, instrument, fast=5, slow=20):
        history = self.data[instrument]
        if len(history) < slow:
            return 0
        fast_ma = np.mean(history[-fast:])
        slow_ma = np.mean(history[-slow:])
        if history[-1] > fast_ma and fast_ma > slow_ma:
            return 1
        if history[-1] < fast_ma and fast_ma < slow_ma:
            return -1
        return 0

    def _scaled_position(self, instrument, signal, strength, max_frac=0.35):
        if signal == 0:
            return 0
        limit = self.positionLimits[instrument]
        frac = max(0.10, min(max_frac, strength))
        raw_units = int(round(limit * frac))
        return raw_units if signal > 0 else -raw_units

    def get_positions(self):
        positionLimits = self.positionLimits
        desiredPositions = {instrument: 0 for instrument in positionLimits}

        if self.day < 20:
            return desiredPositions

        signals = {}
        for instrument in positionLimits:
            if instrument in {"Fintech Token", "UQ Dollar", "Boat Party Ticket"}:
                z = self._rolling_zscore(instrument, window=20)
                if z > 1.2:
                    strength = min(0.35, max(0.12, abs(z) / 3.0))
                    signals[instrument] = (-1, strength)
                elif z < -1.2:
                    strength = min(0.35, max(0.12, abs(z) / 3.0))
                    signals[instrument] = (1, strength)
                else:
                    signals[instrument] = (0, 0.0)
            elif instrument in {"Thrifted Jeans", "Sausage Sizzle", "Bread", "Sausage", "MenuDash"}:
                signal = self._trend_signal(instrument, fast=5, slow=20)
                strength = 0.25 if signal != 0 else 0.0
                signals[instrument] = (signal, strength)
            else:
                signals[instrument] = (0, 0.0)

        for instrument, (signal, strength) in signals.items():
            desiredPositions[instrument] = self._scaled_position(instrument, signal, strength)

        # Keep overall notional exposure well below the hard budget cap.
        notional = 0
        for instrument in desiredPositions:
            notional += abs(desiredPositions[instrument]) * self.get_current_price(instrument)

        if notional > 400000:
            scale = 400000 / max(notional, 1e-9)
            for instrument in desiredPositions:
                desiredPositions[instrument] = int(round(desiredPositions[instrument] * scale))
                if desiredPositions[instrument] != 0 and abs(desiredPositions[instrument]) < 1:
                    desiredPositions[instrument] = 0

        return desiredPositions
