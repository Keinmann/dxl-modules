import './App.scss'
import TcpSocket from 'react-native-tcp-socket'

function App() {

  const tcpOptions = {
    port: 8117,
    host: "192.168.42.117",
    localAddress: '192.168.42.217',
    reuseAddress: true
  };


  return (
    <>
      <h1>DxlModules</h1>
    </>
  )
}

export default App
