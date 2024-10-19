import { Player } from "@lottiefiles/react-lottie-player";
import "../static/styles/Home.css";

const Home = () => {
  return (
    <div className="index-hero">
      <div className="hero-title">
        <h1 className="hero-text">Device Recommendation System</h1>
        <p className="hero-subtext">
          A site for recommending devices to people based on what they prefer.
        </p>
      </div>
      <Player
        src="https://lottie.host/912bb395-4c2c-4e1b-8538-ff1f5610cfa3/qsDTE61aMm.json"
        loop
        autoplay
        className="player"
      ></Player>
    </div>
  );
};

export default Home;
