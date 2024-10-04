import { useState } from "react";
import { useAppSelector, useAppDispatch } from "../app/hooks";
import { decrement, increment } from "../features/counter/counterSlice";
import { FiPlus, FiMinus } from "react-icons/fi"; // Importing icons from React Icons

export function Counter() {
  // The `state` arg is correctly typed as `RootState` already
  const count = useAppSelector((state) => state.counter.value);
  const dispatch = useAppDispatch();
  const [isAnimating, setIsAnimating] = useState(false);

  const handleIncrement = () => {
    setIsAnimating(true);
    dispatch(increment());
    setTimeout(() => setIsAnimating(false), 300); // Animation duration
  };

  const handleDecrement = () => {
    setIsAnimating(true);
    dispatch(decrement());
    setTimeout(() => setIsAnimating(false), 300);
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <h1 className="text-2xl font-bold">Counter</h1>
      <div className="flex items-center space-x-4">
        <button
          className="p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition duration-300"
          onClick={handleDecrement}
        >
          <FiMinus className="w-5 h-5" />
        </button>
        <span
          className={`text-3xl font-semibold ${
            isAnimating ? "animate-pulse" : ""
          }`}
        >
          {count}
        </span>
        <button
          className="p-2 bg-green-500 text-white rounded-full hover:bg-green-600 transition duration-300"
          onClick={handleIncrement}
        >
          <FiPlus className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
