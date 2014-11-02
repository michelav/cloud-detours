package br.unifor.ppgia.cloud.core.comm;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import java.util.Random;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import br.unifor.ppgia.cloud.core.comm.ChannelProvider.EventType;
import br.unifor.ppgia.cloud.core.comm.defaultimpl.DefaultChannelProvider;

public class ChannelTests {
	
	/*
	 * You should start loopback.py program before running
	 * tests.
	 */
	
	Channel channel;
	final static String ENDPOINT = "ipc:///tmp/tests.ipc";  

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
//		Runtime rt = Runtime.getRuntime();
//		rt.exec("tests/loopback.py " + ENDPOINT);
	}

	@AfterClass
	public static void tearDownAfterClass() throws Exception {
//		ChannelProvider channelProvider = DefaultChannelProvider.getInstance();
//		Channel control = channelProvider.createChannel(ENDPOINT);
//		control.sendEvent(channelProvider.getEvent(EventType.TERMINATE_EVT));
//		control.close();
	}

	@Before
	public void setUp() throws Exception {
		ChannelProvider channelProvider = DefaultChannelProvider.getInstance();
		channel = channelProvider.createChannel(ENDPOINT);
	}

	@After
	public void tearDown() throws Exception {
		channel.close();
	}

	@Test
	public void simpleSendAndRecvTest() {
		ChannelProvider channelProvider = DefaultChannelProvider.getInstance();
		Event ping = channelProvider.getEvent(EventType.PING_EVT);
		channel.sendEvent(ping);

		Event pong = channel.recvEvent();

		assertEquals("Ping request is not working on IPC Channels...", "pong",
				pong.getInfo("control"));
	}

	@Test
	public void sendAndRecvWithDataTest() {
		ChannelProvider channelProvider = DefaultChannelProvider.getInstance();
		Event loop = channelProvider.getEvent(EventType.LOOPBACK_EVT);
		byte[] payload = new byte[20];
		new Random().nextBytes(payload);

		loop.setPayload(payload);
		channel.sendEvent(loop);
		Event back = channel.recvEvent();

		assertEquals("LoopBack message is not working on IPC Channels...",
				"back", back.getInfo("control"));
		assertArrayEquals("LoopBack message is not working on IPC Channels...",
				payload, back.getPayload());
	}
}
